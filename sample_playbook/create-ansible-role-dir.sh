#!/bin/bash

# Script to create ansible playbook directories

# define your roles here
roles=(common ospf_leaf  ospf_spine upgrade_sw)
directories=(tasks handlers files default vars templates)

# create playbook
#mkdir global_vars

for i in ${roles[@]}; do
for j in ${directories[@]}; do
  mkdir -p roles/${i}/${j}
done
done
exit 0

