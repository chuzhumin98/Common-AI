#pragma once
#include "Point.h"
class TreeNode
{
public:
	Point* point; //记录该节点时所走的位置
	int father; //父节点
	int* children; //子节点们
	int childrenMaxIndex; //子节点中最大的索引位置
	bool isMyStep; //存储该步是不是我方走，true为我方走，false为对方走
	bool isLeaf; //判断是否为叶节点

public:
	TreeNode(void);
	TreeNode(int x, int y, bool isMySteps, int fatherIndex);
	~TreeNode(void);
};

