# -*- coding: utf-8 -*-
# Copyright 2020 Red Hat
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)


"""
The index_of filter plugin
"""
from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = """
    name: xml_to_json
    author: Ashwini Mhatre (@amhatre)
    version_added: "1.0.0"
    short_description: convert given xml string to json
    description:
        - This plugin converts the xml string to json.
        - Using the parameters below- C(data|ansible.utils.xml_to_json)
    options:
      data:
        description:
        - The input xml string .
        - This option represents the xml value that is passed to the filter plugin in pipe format.
        - For example C(config_data|ansible.utils.xml_to_json), in this case C(config_data) represents this option.
        type: str
        required: True
    notes:
"""

EXAMPLES = r"""

#### Simple examples

- name: Define xml data 
  ansible.builtin.set_fact:
    xml:
    - 1
    - 2
    - 3

- name: Find the index of 2
  ansible.builtin.set_fact:
    indices: "{{ data|ansible.utils.index_of('eq', 2) }}"

# TASK [Find the index of 2] *************************************************
# ok: [nxos101] => changed=false
#   ansible_facts:
#     indices: '1'


- name: Find the index of 2, ensure list is returned
  ansible.builtin.set_fact:
    indices: "{{ data|ansible.utils.index_of('eq', 2, wantlist=True) }}"

# TASK [Find the index of 2, ensure list is returned] ************************
# ok: [nxos101] => changed=false
#   ansible_facts:
#     indices:
#     - 1


- name: Find the index of 3 using the long format
  ansible.builtin.set_fact:
    indices: "{{ data|ansible.utils.index_of(test='eq', value=value, wantlist=True) }}"
  vars:
    value: 3

# TASK [Find the index of 3 using the long format] ***************************
# ok: [nxos101] => changed=false
#   ansible_facts:
#     indices:
#     - 2


- name: Find numbers greater than 1, using loop
  debug:
    msg: "{{ data[item] }} is {{ test }} than {{ value }}"
  loop: "{{ data|ansible.utils.index_of(test, value) }}"
  vars:
    test: '>'
    value: 1

# TASK [Find numbers great than 1, using loop] *******************************
# ok: [sw01] => (item=1) =>
#   msg: 2 is > than 1
# ok: [sw01] => (item=2) =>
#   msg: 3 is > than 1


#### Working with lists of dictionaries

- name: Define a list with hostname and type
  ansible.builtin.set_fact:
    data:
    - name: sw01.example.lan
      type: switch
    - name: rtr01.example.lan
      type: router
    - name: fw01.example.corp
      type: firewall
    - name: fw02.example.corp
      type: firewall

- name: Find the index of all firewalls using the type key
  ansible.builtin.set_fact:
    firewalls: "{{ data|ansible.utils.index_of('eq', 'firewall', 'type') }}"

# TASK [Find the index of all firewalls using the type key] ******************
# ok: [nxos101] => changed=false
#   ansible_facts:
#     firewalls:
#     - 2
#     - 3

- name: Find the index of all firewalls, use in a loop
  debug:
    msg: "The type of {{ device_type }} at index {{ item }} has name {{ data[item].name }}."
  loop: "{{ data|ansible.utils.index_of('eq', device_type, 'type') }}"
  vars:
    device_type: firewall

# TASK [Find the index of all firewalls, use in a loop, as a filter] *********
# ok: [nxos101] => (item=2) =>
#   msg: The type of firewall at index 2 has name fw01.example.corp.
# ok: [nxos101] => (item=3) =>
#   msg: The type of firewall at index 3 has name fw02.example.corp.

- name: Find the index of all devices with a .corp name
  debug:
    msg: "The device named {{ data[item].name }} is a {{ data[item].type }}"
  loop: "{{ data|ansible.utils.index_of('regex', expression, 'name') }}"
  vars:
    expression: '\.corp$' # ends with .corp

# TASK [Find the index of all devices with a .corp name] *********************
# ok: [nxos101] => (item=2) =>
#   msg: The device named fw01.example.corp is a firewall
# ok: [nxos101] => (item=3) =>
#   msg: The device named fw02.example.corp is a firewall


#### Working with complex structures from resource modules

- name: Retrieve the current L3 interface configuration
  cisco.nxos.nxos_l3_interfaces:
    state: gathered
  register: current_l3

# TASK [Retrieve the current L3 interface configuration] *********************
# ok: [sw01] => changed=false
#   gathered:
#   - name: Ethernet1/1
#   - name: Ethernet1/2
#   <...>
#   - name: Ethernet1/128
#   - ipv4:
#     - address: 192.168.101.14/24
#     name: mgmt0

- name: Find the indices interfaces with a 192.168.101.xx ip address
  ansible.builtin.set_fact:
    found: "{{ found + entry }}"
  with_indexed_items: "{{ current_l3.gathered }}"
  vars:
    found: []
    ip: '192.168.101.'
    address: "{{ item.1.ipv4|d([])|ansible.utils.index_of('search', ip, 'address', wantlist=True) }}"
    entry:
    - interface_idx: "{{ item.0 }}"
      address_idxs: "{{ address }}"
  when: address

# TASK [debug] ***************************************************************
# ok: [sw01] =>
#   found:
#   - address_idxs:
#     - 0
#     interface_idx: '128'

- name: Show all interfaces and their address
  debug:
    msg: "{{ interface.name }} has ip {{ address }}"
  loop: "{{ found|subelements('address_idxs') }}"
  vars:
    interface: "{{ current_l3.gathered[item.0.interface_idx|int] }}"
    address: "{{ interface.ipv4[item.1].address }}"

# TASK [Show all interfaces and their address] *******************************
# ok: [nxos101] => (item=[{'interface_idx': '128', 'address_idxs': [0]}, 0]) =>
#   msg: mgmt0 has ip 192.168.101.14/24


#### Working with deeply nested data

- name: Define interface configuration facts
  ansible.builtin.set_fact:
    data:
      interfaces:
        interface:
          - config:
              description: configured by Ansible - 1
              enabled: True
              loopback-mode: False
              mtu: 1024
              name: loopback0000
              type: eth
            name: loopback0000
            subinterfaces:
              subinterface:
                - config:
                    description: subinterface configured by Ansible - 1
                    enabled: True
                    index: 5
                  index: 5
                - config:
                    description: subinterface configured by Ansible - 2
                    enabled: False
                    index: 2
                  index: 2
          - config:
              description: configured by Ansible - 2
              enabled: False
              loopback-mode: False
              mtu: 2048
              name: loopback1111
              type: virt
            name: loopback1111
            subinterfaces:
              subinterface:
                - config:
                    description: subinterface configured by Ansible - 3
                    enabled: True
                    index: 10
                  index: 10
                - config:
                    description: subinterface configured by Ansible - 4
                    enabled: False
                    index: 3
                  index: 3


- name: Find the description of loopback111, subinterface index 10
  debug:
    msg: |-
      {{ data.interfaces.interface[int_idx|int]
          .subinterfaces.subinterface[subint_idx|int]
            .config.description }}
  vars:
    # the values to search for
    int_name: loopback1111
    sub_index: 10
    # retrieve the index in each nested list
    int_idx: |
      {{ data.interfaces.interface|
            ansible.utils.index_of('eq', int_name, 'name') }}
    subint_idx: |
      {{ data.interfaces.interface[int_idx|int]
            .subinterfaces.subinterface|
                ansible.utils.index_of('eq', sub_index, 'index') }}

# TASK [Find the description of loopback111, subinterface index 10] ************
# ok: [sw01] =>
#   msg: subinterface configured by Ansible - 3

"""

from ansible.errors import AnsibleFilterError
from jinja2.filters import environmentfilter
from ansible_collections.ansible.utils.plugins.module_utils.common.xml_to_json import (
    xml_to_json,
)
from ansible_collections.ansible.utils.plugins.module_utils.common.argspec_validate import (
    AnsibleArgSpecValidator,
)


@environmentfilter
def _xml_to_json(*args, **kwargs):
    """Convert the given data from xml to json."""

    keys = [
        "environment",
        "data",
    ]
    data = dict(zip(keys, args))
    data.update(kwargs)
    environment = data.pop("environment")
    aav = AnsibleArgSpecValidator(
        data=data, schema=DOCUMENTATION, name="xml_to_json"
    )
    valid, errors, updated_data = aav.validate()
    if not valid:
        raise AnsibleFilterError(errors)
    updated_data["tests"] = environment.tests
    return xml_to_json(**updated_data)


class FilterModule(object):
    """ xml_to_json  """

    def filters(self):
        """a mapping of filter names to functions"""
        return {"xml_to_json": _xml_to_json}