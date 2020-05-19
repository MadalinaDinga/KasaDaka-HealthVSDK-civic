import logging

from django.http import Http404
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse
from ..models import VoiceService, lookup_or_create_session, lookup_kasadaka_user_by_caller_id
from . import base

logger = logging.getLogger("mada")


def get_caller_id_from_GET_request(request):
    if 'caller_id' in request.GET:
        return request.GET['caller_id']
    elif 'callerid' in request.GET:
        return request.GET['callerid']
    return None


def voice_service_start(request, voice_service_id, session_id=None):
    logger.debug("Voice service with id {} - Request {} - Session id {}".format(voice_service_id, request, session_id))
    voice_service = get_object_or_404(VoiceService, pk=voice_service_id)

    if not voice_service.active:
        # TODO give a nicer error message
        raise Http404("Inactive service")

    caller_id = get_caller_id_from_GET_request(request)
    session = lookup_or_create_session(voice_service, session_id, caller_id)
    logger.debug("Caller ID {} - Session {}".format(caller_id, session))

    if voice_service.is_pass_based_auth:

        logger.debug("Password-based authentication is set")
        if not session.language:
            return select_session_language(voice_service, session, caller_id)
        logger.debug("Session language {}".format(session.language))

        logger.debug("Start authentication process if required or preferred")
        if voice_service.registration_preferred_or_required:
            logger.debug("User authentication started")
            return password_based_auth(session)
        logger.debug("User authentication finished")
    else:
        logger.debug("CallerID-based authentication is set")
        if voice_service.registration_preferred_or_required:
            logger.debug("User authentication started")
            redirect_url = callerID_auth(voice_service, session, caller_id)
            logger.debug("Redirect url".format(redirect_url))
            if redirect_url is not None:
                return redirect_url
        logger.debug("User authentication finished")

        # If not set, select language
        if not session.language:
            logger.debug("Perform language selection")
            return select_session_language(voice_service, session, caller_id)
        logger.debug("Session language is {}".format(session.language))

    logger.debug("Redirecting to start element {}".format(voice_service.start_element))
    return base.redirect_to_voice_service_element(voice_service.start_element, session)


def select_session_language(voice_service, session=None, caller_id=None):
    """
        Starting point for a voice service. Looks up user (redirects to registation
        otherwise), creates session, (redirects to language selection).
        If all requirements are fulfilled, redirects to the starting element of the
        voice service.
    """
    logger.debug(
        "Language selection started for Voice service {} - Session {} - CallerID {}".format(voice_service, session,
                                                                                            caller_id))

    # Redirect the user to language selection for this session only.
    # Make sure to return to start of voice service after selection of language
    return_url = reverse('service-development:voice-service', args=[session.service.id, session.id])
    return base.redirect_add_get_parameters('service-development:language-selection',
                                            session.id,
                                            redirect_url=return_url)


def password_based_auth(session):
    # Authenticates a user and links the session to the user if auth was successful (valid credentials were given)
    logger.debug("Authenticated user {}".format(session.user))
    logger.debug("Current session information {}".format(session))
    return_url = reverse('service-development:voice-service', args=[session.service.id, session.id])
    return base.redirect_add_get_parameters('service-development:kasadaka-user-auth',
                                            session.id,
                                            redirect_url=return_url)


def callerID_auth(voice_service, session=None, caller_id=None):
    """
        Starting point for a voice service. Looks up user (redirects to registation
        otherwise), creates session, (redirects to language selection).
        If all requirements are fulfilled, redirects to the starting element of the
        voice service.
    """
    logger.debug(
        "CallerID-based authentication started for Voice service {} - Session {} - CallerID {}".format(voice_service,
                                                                                                       session,
                                                                                                       caller_id))
    # If there is no caller_id provided, and user registration is required for this service,
    # throw an error
    if voice_service.registration_required and not caller_id:
        # TODO make this into a nice audio error
        raise ValueError(
            'This service requires registration, but registration is not possible, because there is no callerID!')

    # If the session is not yet linked to an user, try to look up the user by
    # Caller ID, and link it to the session. If the user cannot be found,
    # redirect to registration.
    if caller_id and not session.user:
        found_user = lookup_kasadaka_user_by_caller_id(caller_id, session.service)
        if found_user:
            session.link_to_user(found_user)
            logger.debug("Session user {}".format(session.user))
            return None
        # If there is no user with this caller_id and registration of users is preferred or required, redirect to registration
        else:
            logger.debug("Register caller id {}".format(caller_id))
            return redirect('service-development:user-registration', session.id)
