import logging
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


def voice_service_start_with_credentials_auth(request, voice_service, session=None, caller_id=None):
    """
        Starting point for a voice service. Looks up user (redirects to registation
        otherwise), creates session, (redirects to language selection).
        If all requirements are fulfilled, redirects to the starting element of the
        voice service.
    """
    logger.debug(
        "Password-based auth started for Voice service {} - Session {} - CallerID {}".format(voice_service, session,
                                                                                             caller_id))
    # if not voice_service.active:
    # TODO give a nicer error message
    # raise Http404()

    if voice_service.registration_required and not caller_id:
        logger.error(
            'This service requires authentication, but authentication is not possible, because there is no callerID!')
        raise ValueError(
            'This service requires authentication, but authentication is not possible, because there is no callerID!')

    # If the language for this session can not be determined,
    # redirect the user to language selection for this session only.
    if not session.language:
        # After selection of language, return to start of voice service.
        logger.debug("Setting language")
        return_url = reverse('service-development:voice-service', args=[session.service.id, session.id])
        return base.redirect_add_get_parameters('service-development:language-selection',
                                                session.id,
                                                redirect_url=return_url)
    logger.debug("Session language {}".format(session.language))

    # Authenticate user - link the session to a user using the given (validated) credentials
    if not session.user:
        logger.debug("Authenticating user")
        return_url = reverse('service-development:voice-service', args=[session.service.id, session.id])
        return base.redirect_add_get_parameters('service-development:kasadaka-user-auth',
                                                session.id,
                                                redirect_url=return_url)
    logger.debug("Auth user {}".format(session.user))


def voice_service_with_callerID_auth(request, voice_service, session=None, caller_id=None):
    """
        Starting point for a voice service. Looks up user (redirects to registation
        otherwise), creates session, (redirects to language selection).
        If all requirements are fulfilled, redirects to the starting element of the
        voice service.
    """
    logger.debug(
        "Password-based auth started for Voice service {} - Session {} - CallerID {}".format(voice_service, session,
                                                                                             caller_id))
    # if not voice_service.active:
    # TODO give a nicer error message
    # raise Http404()

    # If the session is not yet linked to an user, try to look up the user by
    # Caller ID, and link it to the session. If the user cannot be found,
    # redirect to registration.
    if caller_id and not session.user:
        found_user = lookup_kasadaka_user_by_caller_id(caller_id, session.service)
        if found_user:
            session.link_to_user(found_user)
            logger.debug("Session user {}".format(session.user))

        # If there is no user with this caller_id and registration of users is preferred or required, redirect to registration
        elif voice_service.registration_preferred_or_required:
            return redirect('service-development:user-registration',
                            session.id)

    # If there is no caller_id provided, and user registration is required for this service,
    # throw an error
    elif voice_service.registration_required and not caller_id:
        # TODO make this into a nice audio error
        raise ValueError(
            'This service requires registration, but registration is not possible, because there is no callerID!')

    # If the language for this session can not be determined,
    # redirect the user to language selection for this session only.
    if not session.language:
        # After selection of language, return to start of voice service.
        return_url = reverse('service-development:voice-service', args=[session.service.id, session.id])
        return base.redirect_add_get_parameters('service-development:language-selection',
                                                session.id,
                                                redirect_url=return_url)
    logger.debug("Session language {}".format(session.language))


def voice_service_start(request, voice_service_id, session_id=None):
    logger.debug("Voice service with id {} - Request {} - Session id {}".format(voice_service_id, request, session_id))
    voice_service = get_object_or_404(VoiceService, pk=voice_service_id)

    caller_id = get_caller_id_from_GET_request(request)
    session = lookup_or_create_session(voice_service, session_id, caller_id)
    logger.debug("Caller ID {} - Session {}".format(caller_id, session))

    if voice_service.registration_required and voice_service.is_pass_based_auth:
        logger.debug("Password-based authentication is set")
        voice_service_start_with_credentials_auth(request, voice_service, session, caller_id)
    else:
        logger.debug("CallerID-based authentication is set")
        voice_service_with_callerID_auth(request, voice_service, session, caller_id)

    return base.redirect_to_voice_service_element(voice_service.start_element, session)
