#!/usr/bin/env python
# coding=utf-8

arr = [31, 41, 59, 26, 41, 58]

for index,num in enumerate(arr):
    t_index = index

    for i in range(index):
        if num < arr[i]:
            t_index = i
            break

    if t_index != index:
        for i in range(index, t_index, -1):
            arr[index] = arr[index - 1]
        arr[t_index] = num

print arr

