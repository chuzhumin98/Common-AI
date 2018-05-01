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
	bool myWin; //我方是否获胜，仅对叶节点讨论
	double winTimes; //该节点上获胜的次数（针对我方而言）
	int totalTimes; //该节点上下棋的总次数
public:
	TreeNode(void);
	TreeNode(int x, int y, bool isMySteps, int fatherIndex);
	~TreeNode(void);
};

