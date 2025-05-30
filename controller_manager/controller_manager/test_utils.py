# Copyright (c) 2024 AIT - Austrian Institute of Technology GmbH
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
#    * Redistributions of source code must retain the above copyright
#      notice, this list of conditions and the following disclaimer.
#
#    * Redistributions in binary form must reproduce the above copyright
#      notice, this list of conditions and the following disclaimer in the
#      documentation and/or other materials provided with the distribution.
#
#    * Neither the name of the {copyright_holder} nor the names of its
#      contributors may be used to endorse or promote products derived from
#      this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE
# LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
# INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
# CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
# ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.
#
# Author: Christoph Froehlich

import time

from launch_testing_ros import WaitForTopics
from sensor_msgs.msg import JointState
from controller_manager.controller_manager_services import list_controllers


def check_node_running(node, node_name, timeout=5.0):
    """
    Checks if a node with the specified name is running within a given timeout.

    Args:
      node (Node): The ROS 2 node instance to use for discovering nodes.
      node_name (str): The name of the node to check for.
      timeout (float, optional): The maximum time to wait for the node to appear, in seconds. Defaults to 5.0.

    Raises:
      AssertionError: If the node with the specified name is not found within the timeout period.
    """

    start = time.time()
    found = False
    while time.time() - start < timeout and not found:
        found = node_name in node.get_node_names()
        time.sleep(0.1)
    assert found, f"{node_name} not found!"


def check_controllers_running(node, cnames, namespace="", state="active", timeout=10.0):
    """
    Check if the specified controllers are running on the given node.

    Args:
      node (Node): The ROS 2 node instance to use for discovering controllers.
      cnames (list of str): List of controller names to check.
      namespace (str, optional): The namespace in which to look for controllers. Defaults to "".
      state (str, optional): The desired state of the controllers. Defaults to "active".
      timeout (float, optional): The maximum time to wait for the node to appear, in seconds. Defaults to 10.0.

    Raises:
      AssertionError: If any of the specified controllers are not found or not in the desired state within the timeout period.
    """

    # wait for controller to be loaded before we call the CM services
    found = {cname: False for cname in cnames}  # Define 'found' as a dictionary
    start = time.time()
    # namespace is either "/" (empty) or "/ns" if set
    if namespace:
        namespace_api = namespace
        if not namespace_api.startswith("/"):
            namespace_api = "/" + namespace_api
        if namespace.endswith("/"):
            namespace_api = namespace_api[:-1]
    else:
        namespace_api = "/"

    while time.time() - start < timeout and not all(found.values()):
        node_names_namespaces = node.get_node_names_and_namespaces()
        for cname in cnames:
            if any(name == cname and ns == namespace_api for name, ns in node_names_namespaces):
                found[cname] = True
        time.sleep(0.1)
    assert all(
        found.values()
    ), f"Controller node(s) not found: {', '.join(['ns: ' + namespace_api + ', ctrl:' + cname for cname, is_found in found.items() if not is_found])}, but seeing {node.get_node_names_and_namespaces()}"

    found = {cname: False for cname in cnames}  # Define 'found' as a dictionary
    start = time.time()
    # namespace is either "/" (empty) or "/ns" if set
    if not namespace:
        cm = "controller_manager"
    else:
        if namespace.endswith("/"):
            cm = namespace + "controller_manager"
        else:
            cm = namespace + "/controller_manager"
    while time.time() - start < timeout and not all(found.values()):
        controllers = list_controllers(node, cm, 5.0).controller
        assert controllers, "No controllers found!"
        for c in controllers:
            for cname in cnames:
                if c.name == cname and c.state == state:
                    found[cname] = True
                    break
        time.sleep(0.1)

    assert all(
        found.values()
    ), f"Controller(s) not found or not {state}: {', '.join([cname for cname, is_found in found.items() if not is_found])}"


def check_if_js_published(topic, joint_names):
    """
    Check if a JointState message is published on a given topic with the expected joint names.

    Args:
      topic (str): The name of the topic to check.
      joint_names (list of str): The expected joint names in the JointState message.

    Raises:
      AssertionError: If the topic is not found, the number of joints in the message is incorrect,
              or the joint names do not match the expected names.
    """
    wait_for_topics = WaitForTopics([(topic, JointState)], timeout=20.0)
    assert wait_for_topics.wait(), f"Topic '{topic}' not found!"
    msgs = wait_for_topics.received_messages(topic)
    msg = msgs[0]
    assert len(msg.name) == len(joint_names), "Wrong number of joints in message"
    # use a set to compare the joint names, as the order might be different
    assert set(msg.name) == set(joint_names), "Wrong joint names"
    wait_for_topics.shutdown()
