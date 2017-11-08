# -*- coding: utf-8 -*-
from rest_framework import status
from rest_framework.exceptions import APIException


class NeighborV4NotFoundError(APIException):
    status_code = status.HTTP_404_NOT_FOUND

    def __init__(self, msg):
        self.detail = u'NeighborV4 %s do not exist.' % (msg)


class NeighborV4Error(APIException):
    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR

    def __init__(self, msg):
        self.detail = msg


class NeighborV4AlreadyCreated(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = u'NeighborV4 already created.'

    def __init__(self, msg=None):
        self.detail = u'NeighborV4 %s already created.' % msg


class NeighborV4NotCreated(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = u'NeighborV4 not created.'

    def __init__(self, msg=None):
        self.detail = u'NeighborV4 %s not created.' % msg


class NeighborV4DoesNotExistException(APIException):
    status_code = status.HTTP_404_NOT_FOUND
    default_detail = u'NeighborV4 does not exists.'


class NeighborV6NotFoundError(APIException):
    status_code = status.HTTP_404_NOT_FOUND

    def __init__(self, msg):
        self.detail = u'NeighborV6 %s do not exist.' % (msg)


class NeighborV6Error(APIException):
    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR

    def __init__(self, msg):
        self.detail = msg


class NeighborV6AlreadyCreated(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = u'NeighborV6 already created.'

    def __init__(self, msg=None):
        self.detail = u'NeighborV6 %s already created.' % msg


class NeighborV6NotCreated(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = u'NeighborV6 not created.'

    def __init__(self, msg=None):
        self.detail = u'NeighborV6 %s not created.' % msg


class NeighborV6DoesNotExistException(APIException):
    status_code = status.HTTP_404_NOT_FOUND
    default_detail = u'NeighborV6 does not exists.'


class LocalIpAndRemoteIpAreInDifferentVrfsException(APIException):
    status_code = status.HTTP_400_BAD_REQUEST

    def __init__(self, neighbor):
        self.detail = u'LocalIp id = {} and RemoteIp id = {} are in ' \
                      u'different Vrfs.'.\
            format(neighbor.local_ip, neighbor.remote_ip)


class LocalIpAndLocalAsnAtDifferentEquipmentsException(APIException):
    status_code = status.HTTP_400_BAD_REQUEST

    def __init__(self, neighbor):
        self.detail = u'LocalIp id = {} and LocalAsn id = {} belongs to ' \
                      u'different Equipments.'.\
            format(neighbor.local_ip, neighbor.local_asn)


class RemoteIpAndRemoteAsnAtDifferentEquipmentsException(APIException):
    status_code = status.HTTP_400_BAD_REQUEST

    def __init__(self, neighbor):
        self.detail = u'RemoteIp id = {} and RemoteAsn id = {} belongs to ' \
                      u'different Equipments.'.\
            format(neighbor.remote_ip, neighbor.remote_asn)


class LocalIpAndPeerGroupAtDifferentEnvironmentsException(APIException):
    status_code = status.HTTP_400_BAD_REQUEST

    def __init__(self, neighbor):
        self.detail = u'LocalIp id = {} and PeerGroup id = {} belongs to ' \
                      u'different Environments.'. \
            format(neighbor.local_ip, neighbor.peer_group)


class NeighborDuplicatedException(APIException):
    status_code = status.HTTP_400_BAD_REQUEST

    def __init__(self, neighbor):
        self.detail = u'It already exists Neighbor with LocalAsn id = {}, ' \
                      u'LocalIp id = {}, RemoteAsn id = {} and ' \
                      u'RemoteIp id = {}'.\
            format(neighbor.local_asn, neighbor.local_ip,
                   neighbor.remote_asn, neighbor.remote_ip)
