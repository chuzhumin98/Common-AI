#include "TreeNode.h"


TreeNode::TreeNode(void)
{
	this->children = new int [12];
	this->point = new Point(-1, -1);
	this->childrenMaxIndex = 0; //该位置取不到
}


TreeNode::TreeNode(int x, int y, bool isMySteps, int fatherIndex) {
	this->point = new Point(x, y);
	this->children = new int [12];
	this->childrenMaxIndex = 0;
	this->isMyStep = isMySteps;
	this->father = fatherIndex;
}

TreeNode::~TreeNode(void)
{
	delete point;
	delete []children;
}
