#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#

from __future__ import annotations
from copy import copy, deepcopy
from dataclasses import dataclass
from typing import List
from collections import deque
from graphviz import Graph
from argparse import ArgumentParser, Namespace

__version__ = "0.0.1"

@dataclass(init=True, frozen=True)
class HanoiTowerDisk:
    """Класс диска"""
    size : int

class HanoiTowerRod:
    """Класс стержня"""
    def __init__(self, disks : deque[HanoiTowerDisk] = deque()) -> None:
        self.__disks : deque[HanoiTowerDisk] = disks
        assert self.__check_order(), "disks order error"
        self.__hash : int = 0
        self.__calc_hash()
        return

    def __eq__(self, other : HanoiTowerRod) -> bool:
        if (len(self.__disks) != len(other.__disks)):
            return False
        return all(self.__disks[i] == other.__disks[i] for i in range(len(self.__disks)))

    def __str__(self) -> str:
        s = ""
        for disk in self.__disks:
            s += f"{disk.size}"
        return s

    def __calc_hash(self) -> None:
        self.__hash = 0
        for disk in self.__disks:
            self.__hash += hash(disk.size)
        return

    def __hash__(self) -> int:
        return self.__hash

    def __check_order(self) -> bool:
        if (len(self.__disks) < 2):
            return True
        for i in range(len(self.__disks)-1):
            if (self.__disks[i].size <= self.__disks[i+1].size):
                return False
        return True

    def can_shift_to(self, dst : HanoiTowerRod) -> bool:
        if (len(self.__disks) == 0):
            return False
        if (len(dst.__disks) == 0):
            return True
        return (self.__disks[-1].size < dst.__disks[-1].size)

    def shift_to(self, dst : HanoiTowerRod) -> None:
        dst.__disks.append(self.__disks.pop())
        return

class HanoiTower:
    def __init__(self, rods : List[HanoiTowerRod]) -> None:
        self.__rods : List[HanoiTowerRod] = rods
        self.__hash : int = 0
        self.__calc_hash()
        return

    def __str__(self) -> str:
        s = ""
        for rod in self.__rods:
            s += f"_{rod}"
        return s

    def __calc_hash(self) -> None:
        self.__hash = 0
        for rod in self.__rods:
            self.__hash += hash(rod)
        return

    def __hash__(self) -> int:
        return self.__hash

    def __eq__(self, other : "HanoiTower") -> bool:
        for i in range(len(self.__rods)):
            if (self.__rods[i] != other.__rods[i]):
                return False
        return True

    def neighbours(self) -> List[HanoiTower]:
        neighbours : List[HanoiTower] = []
        for rod_src_i in range(len(self.__rods)):
            for rod_dst_i in range(len(self.__rods)):
                if (rod_src_i == rod_dst_i):
                    continue
                rod_src = self.__rods[rod_src_i]
                rod_dst = self.__rods[rod_dst_i]
                if (rod_src.can_shift_to(rod_dst)):
                    rods = []
                    for rod in self.__rods:
                        rods.append(deepcopy(rod))
                    rods[rod_src_i].shift_to(rods[rod_dst_i])
                    tower = HanoiTower(rods)
                    neighbours.append(tower)
        return neighbours

class HanoiTowerNode:
    def __init__(self, tower : HanoiTower) -> None:
        self.__tower : HanoiTower = tower
        self.__edges : List[HanoiTowerEdge] = []
        return

    def __eq__(self, other : HanoiTowerNode) -> bool:
        return (self.__tower == other.__tower)

    def __str__(self) -> str:
        return f"NODE: EDGES={len(self.__edges)} TOWER={self.__tower}"

    def add_edge(self, edge : HanoiTowerEdge) -> None:
        for e in self.__edges:
            if (e == edge):
                return
        self.__edges.append(edge)
        return

    def tower(self) -> HanoiTower:
        return self.__tower

class HanoiTowerEdge:
    def __init__(self, node1 : HanoiTowerNode, node2 : HanoiTowerNode) -> None:
        self.__node1 = node1
        self.__node2 = node2
        return

    def __str__(self) -> str:
        n1 = self.__node1
        n2 = self.__node2
        return f"EDGE {n1} <-> {n2}"

    def __eq__(self, other : HanoiTowerEdge) -> bool:
        sn1 = self.__node1
        on1 = other.__node1
        sn2 = self.__node2
        on2 = other.__node2
        return (((sn1 == on1) and (sn2 == on2)) or ((sn1 == on2) and (sn2 == on1)))

    def node1(self) -> HanoiTowerNode:
        return self.__node1

    def node2(self) -> HanoiTowerNode:
        return self.__node2

class HanoiTowerGraph:
    def __init__(self, disks_count : int = 3, rods_count : int = 3) -> None:
        self.__disks_count = disks_count
        self.__rods_count = rods_count
        self.__nodes : List[HanoiTowerNode] = []
        self.__nodes_frontier : List[HanoiTowerNode] = []
        self.__edges : List[HanoiTowerEdge] = []
        self.__step_count : int = 0
        return

    def add_origin(self) -> None:
        rods : List[HanoiTowerRod] = []
        for r_i in range(self.__rods_count):
            disks : deque[HanoiTowerDisk] = deque()
            if (r_i == 0):
                for d_i in range(self.__disks_count):
                    disks.append(HanoiTowerDisk(self.__disks_count - d_i))
            rod = HanoiTowerRod(disks)
            rods.append(rod)
        tower = HanoiTower(rods)
        node = HanoiTowerNode(tower)
        self.__nodes = []
        self.__nodes_frontier = []
        self.__nodes.append(node)
        self.__nodes_frontier.append(node)
        return

    def has_node(self, n : HanoiTowerNode) -> bool:
        for node in self.__nodes:
            if (node == n):
                return True
        return False

    def has_edge(self, e : HanoiTowerEdge) -> bool:
        for edge in self.__edges:
            if (edge == e):
                return True
        return False

    def step(self) -> bool:
        self.__step_count += 1
        print(f"STEP {self.__step_count}")
        nodes_frontier = self.__nodes_frontier
        self.__nodes_frontier = []
        nodes_added : bool = False
        edges_added : bool = False
        for node in nodes_frontier:
            neighbours = node.tower().neighbours()
            for neighbour in neighbours:
                neighbour_node = HanoiTowerNode(neighbour)
                edge = HanoiTowerEdge(node, neighbour_node)
                if (not self.has_edge(edge)):
                    edges_added = True
                    self.__edges.append(edge)
                node.add_edge(edge)
                neighbour_node.add_edge(edge)
                if (not self.has_node(neighbour_node)):
                    nodes_added = True
                    self.__nodes.append(neighbour_node)
                    self.__nodes_frontier.append(neighbour_node)
        return nodes_added or edges_added

    def print_nodes(self) -> None:
        print(f"----NODES----")
        for node in self.__nodes:
            print(node)
        return

    def visualize(self) -> None:
        dot = Graph('Hanoi Tower', comment=f'The hanoi tower {self.__rods_count} {self.__disks_count} graph', engine='neato') # circo neato twopi fdp osage sfdp patchwork
        for node in self.__nodes:
            dot.node(f"{node.tower()}", f"*", shape="point")
        for edge in self.__edges:
            dot.edge(f"{edge.node1().tower()}", f"{edge.node2().tower()}")
        dot.render(directory='.', view=True)  
        return

def main() -> None:
    arg_parser = ArgumentParser()
    arg_parser.add_argument("-d", dest="disks_count", default=3, help="number of disks DISKS", metavar="DISKS")
    arg_parser.add_argument("-r", dest="rods_count", default=3, help="number of rods RODS", metavar="RODS")
    arg_parser.add_argument('--version', action='version', version=f"HANOI TOWER GRAPH {__version__}")
    args = arg_parser.parse_args()

    graph = HanoiTowerGraph(int(args.disks_count), int(args.rods_count))
    graph.add_origin()
    while (graph.step()):
        pass
    graph.visualize()
    return

if __name__ == "__main__":
    main()