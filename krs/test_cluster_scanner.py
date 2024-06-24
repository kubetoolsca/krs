import pytest
from unittest.mock import patch
import kubernetes
from kubernetes.client.rest import ApiException  #https://github.com/kubernetes-client/python/blob/master/kubernetes/client/rest.py
from krs.utils.cluster_scanner import KubetoolsScanner

@pytest.fixture
def scanner():
    return KubetoolsScanner()

@patch('kubernetes.client.CoreV1Api.list_namespace')
def test_list_namespaces(mock_list_namespace, scanner):
    mock_list_namespace.return_value.items = [
        type('obj', (object,), {'metadata': type('obj', (object,), {'name': 'default'})})()
    ]
    namespaces = scanner.list_namespaces()
    assert namespaces == ['default']

@patch('kubernetes.client.CoreV1Api.list_namespaced_pod')
def test_list_pods(mock_list_pods, scanner):
    mock_list_pods.return_value.items = [
        type('obj', (object,), {'metadata': type('obj', (object,), {'name': 'pod-1'})})()
    ]
    pods = scanner.list_pods('default')
    assert pods == ['pod-1']

# Additional tests for other methods here...
@patch('kubernetes.client.CoreV1Api.read_namespaced_pod_log')
def test_get_pod_info(mock_read_pod_log, scanner):
    mock_read_pod_log.return_value = "Log data here"
    pod_info = scanner.get_pod_info('default', 'pod-1')
    assert 'Logs' in pod_info
    assert pod_info['Logs'] == {'Log data here'}

@patch('kubernetes.client.CoreV1Api.list_namespaced_event')
def test_fetch_pod_events(mock_list_events, scanner):
    mock_list_events.return_value.items = [
        type('obj', (object,), {'metadata': type('obj', (object,), {'name': 'event-1'}), 'message': 'Test event', 'reason': 'Test reason'})()
    ]
    events = scanner.fetch_pod_events('default', 'pod-1')
    assert events == [{'Name': 'event-1', 'Message': 'Test event', 'Reason': 'Test reason'}]
