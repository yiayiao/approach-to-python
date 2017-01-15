#!/usr/bin/env python
# coding=utf-8

def max_heapify(arr, i, l):
    tmp = arr[i]
    left = i * 2 + 1
    right = i * 2 + 2

    if left < l and arr[left] > tmp:
        tmp = arr[left]
    if right < l and arr[right] > tmp:
        tmp = arr[right]

    if tmp != arr[i]:
        if tmp == arr[left]:
            arr[i], arr[left] = arr[left], arr[i]
            max_heapify(arr, left, l)
        else:
            arr[i], arr[right]= arr[right], arr[i]
            max_heapify(arr, right, l)

def build_max_heap(arr):
    for i in range(len(arr) / 2, -1, -1):
        max_heapify(arr, i, len(arr))

def heap_sort(arr):
    build_max_heap(arr)
    for i in range(len(arr) - 1, 0, -1):
        arr[i], arr[0] = arr[0], arr[i]
        max_heapify(arr, 0, i)

import random
        
def random_int_list(start, stop, length):
    start, stop = (int(start), int(stop)) if start <= stop else (int(stop), int(start))
    length = int(abs(length)) if length else 0
    random_list = []
    for i in range(length):
        random_list.append(random.randint(start, stop))
    return random_list

if __name__ == '__main__':
    arr = random_int_list(0, 20, 10)
    print arr
    heap_sort(arr)
    print arr
    print 'hello world'
