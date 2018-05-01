#include <iostream>
#include <ctime>
#include <conio.h>
#include <atlstr.h>
#include "Point.h"
#include "Strategy.h"
#include "TreeNode.h"

using namespace std;

//type=1:查看该位置是否对我方有所威胁;type=2:查看我方对对方是否有威胁
bool hasThreadInPoint(int x, int y, const int M, const int N, int** board, const int* top, const int noX, const int noY, int type) {
	//考虑纵向连成线
	int bottomIndex = x; //最底端是1的位置
	while (bottomIndex < M-1) {
		if (board[bottomIndex+1][y] != type) {
			break;
		}
		bottomIndex++;
	}
	//_cprintf("(%d,%d) = %d\n", x, y, bottomIndex-x+1);
	if (bottomIndex - x >= 3) {
		return true;
	} 
	//考虑横向连成线
	int liveQi = 0; //两边位置活棋的个数，活棋个数为2时，需要提前进行防守了
	int leftIndex = y; //最左端是1的位置
	while (leftIndex > 0) {
		if (board[x][leftIndex-1] != type) {
			if (board[x][leftIndex-1] == 0 && top[leftIndex-1]-1 == x && (x != noX || leftIndex-1 != noY)) {
				liveQi++;
			}
			break;
		}
		leftIndex--;
	}
	int rightIndex = y; //最右端是1的位置
	while (rightIndex < N-1) {
		if (board[x][rightIndex+1] != type) {
			if (board[x][rightIndex+1] == 0 && top[rightIndex+1]-1 == x && (x != noX || rightIndex+1 != noY)) {
				liveQi++;
			}
			break;
		}
		rightIndex++;
	}
	//_cprintf("(%d,%d) = %d\n", x, y, rightIndex-leftIndex+1);
	if (liveQi == 2 && type == 1) { 
		rightIndex++; //如果活棋的个数为2，则需要提前一步加紧预防
	}
	if (rightIndex - leftIndex >= 3) {
		return true;
	}
	//考虑正斜线连成线
	liveQi = 0; //两边位置活棋的个数，活棋个数为2时，需要提前进行防守了
	int leftDelta = 0; //向左端拓展的个数
	while (y - leftDelta > 0 && x - leftDelta > 0) {
		if (board[x-leftDelta-1][y-leftDelta-1] != type) {
			if (board[x-leftDelta-1][y-leftDelta-1] == 0 && top[y-leftDelta-1]-1 == x-leftDelta-1 && (x-leftDelta-1 != noX || y-leftDelta-1 != noY)) {
				liveQi++;
			}
			break;
		}
		leftDelta++;
	}
	int rightDelta = 0; //向右端扩展的个数
	while (y + rightDelta < N-1 && x + rightDelta < M-1) {
		if (board[x+rightDelta+1][y+rightDelta+1] != type) {
			if (board[x+rightDelta+1][y+rightDelta+1] == 0 && top[y+rightDelta+1]-1 == x+rightDelta+1 && (x+rightDelta+1 != noX || y+rightDelta+1 != noY)) {
				liveQi++;
			}
			break;
		}
		rightDelta++;
	}
	//_cprintf("(%d,%d) = %d\n", x, y, rightIndex-leftIndex+1);
	if (liveQi == 2 && type == 1) { 
		rightDelta++; //如果活棋的个数为2，则需要提前一步加紧预防
	}
	if (rightDelta + leftDelta >= 3) {
		return true;
	}
	//考虑反斜线连成线
	liveQi = 0; //两边位置活棋的个数，活棋个数为2时，需要提前进行防守了
	leftDelta = 0; //向左端拓展的个数
	while (y - leftDelta > 0 && x + leftDelta < M-1) {
		if (board[x+leftDelta+1][y-leftDelta-1] != type) {
			if (board[x+leftDelta+1][y-leftDelta-1] == 0 && top[y-leftDelta-1]-1 == x+leftDelta+1 && (x+leftDelta+1 != noX || y-leftDelta-1 != noY)) {
				liveQi++;
			}
			break;
		}
		leftDelta++;
	}
	rightDelta = 0; //向右端扩展的个数
	while (y + rightDelta < N-1 && x - rightDelta > 0) {
		if (board[x-rightDelta-1][y+rightDelta+1] != type) {
			if (board[x-rightDelta-1][y+rightDelta+1] == 0 && top[y+rightDelta+1]-1 == x-rightDelta-1 && (x-rightDelta-1 != noX || y+rightDelta+1 != noY)) {
				liveQi++;
			}
			break;
		}
		rightDelta++;
	}
	//_cprintf("(%d,%d) = %d\n", x, y, rightIndex-leftIndex+1);
	if (liveQi == 2 && type == 1) { 
		rightDelta++; //如果活棋的个数为2，则需要提前一步加紧预防
	}
	if (rightDelta + leftDelta >= 3) {
		return true;
	}
	return false;
}

/*
	策略函数接口,该函数被对抗平台调用,每次传入当前状态,要求输出你的落子点,该落子点必须是一个符合游戏规则的落子点,不然对抗平台会直接认为你的程序有误
	
	input:
		为了防止对对抗平台维护的数据造成更改，所有传入的参数均为const属性
		M, N : 棋盘大小 M - 行数 N - 列数 均从0开始计， 左上角为坐标原点，行用x标记，列用y标记
		top : 当前棋盘每一列列顶的实际位置. e.g. 第i列为空,则_top[i] == M, 第i列已满,则_top[i] == 0
		_board : 棋盘的一维数组表示, 为了方便使用，在该函数刚开始处，我们已经将其转化为了二维数组board
				你只需直接使用board即可，左上角为坐标原点，数组从[0][0]开始计(不是[1][1])
				board[x][y]表示第x行、第y列的点(从0开始计)
				board[x][y] == 0/1/2 分别对应(x,y)处 无落子/有用户的子/有程序的子,不可落子点处的值也为0
		lastX, lastY : 对方上一次落子的位置, 你可能不需要该参数，也可能需要的不仅仅是对方一步的
				落子位置，这时你可以在自己的程序中记录对方连续多步的落子位置，这完全取决于你自己的策略
		noX, noY : 棋盘上的不可落子点(注:其实这里给出的top已经替你处理了不可落子点，也就是说如果某一步
				所落的子的上面恰是不可落子点，那么UI工程中的代码就已经将该列的top值又进行了一次减一操作，
				所以在你的代码中也可以根本不使用noX和noY这两个参数，完全认为top数组就是当前每列的顶部即可,
				当然如果你想使用lastX,lastY参数，有可能就要同时考虑noX和noY了)
		以上参数实际上包含了当前状态(M N _top _board)以及历史信息(lastX lastY),你要做的就是在这些信息下给出尽可能明智的落子点
	output:
		你的落子点Point
*/
extern "C" __declspec(dllexport) Point* getPoint(const int M, const int N, const int* top, const int* _board, 
	const int lastX, const int lastY, const int noX, const int noY){
	clock_t startTime = clock();

	/*
		不要更改这段代码
	*/
	int x = -1, y = -1;//最终将你的落子点存到x,y中
	int** board = new int*[M];
	for(int i = 0; i < M; i++){
		board[i] = new int[N];
		for(int j = 0; j < N; j++){
			board[i][j] = _board[i * N + j];
		}
	}
	
	/*
		根据你自己的策略来返回落子点,也就是根据你的策略完成对x,y的赋值
		该部分对参数使用没有限制，为了方便实现，你可以定义自己新的类、.h文件、.cpp文件
	*/
	//Add your own code below
	//AllocConsole();
	/*
	for (int i = 0; i < M; i++) {
		for (int j = 0; j < N; j++) {
			_cprintf("%d ",board[i][j]);
		}
		_cprintf("\n");
	}
	*/
	//第一步，先看看有没有必胜的位置
	bool hasThread = false;
	for (int i = 0; i < N; i++) {
		if (top[i] > 0) {
			if (hasThreadInPoint(top[i]-1, i, M, N, board, top, noX, noY, 2)) {
				//有威胁位置直接下在威胁位置上
				x = top[i]-1;
				y = i;
				hasThread = true;
				break;
			}
		}
	}
	//第二步，看看对方有没有威胁自己的位置
	if (!hasThread) {
		for (int i = 0; i < N; i++) {
			if (top[i] > 0) {
				if (hasThreadInPoint(top[i]-1, i, M, N, board, top, noX, noY, 1)) {
					//有威胁位置直接下在威胁位置上
					x = top[i]-1;
					y = i;
					hasThread = true;
					break;
				}
			}
		}
	}

	if (!hasThread) {
		const int STATE_NUM = 2000000;
		TreeNode** states = new TreeNode* [STATE_NUM];
		states[0] = new TreeNode(-1, -1, true, -1); //根节点的父节点设为-1
		int stateSize = 1; //状态空间的大小
		int* currentTop = new int [N]; //当前的top信息

		while (true) {
			clock_t nowTime = clock();
			if (nowTime - startTime >= 2.5 * CLOCKS_PER_SEC || stateSize >= STATE_NUM) {
				break; //达到时间阈值或数组已经填满后即停止扩展
			}
		}

		for (int i = 0; i < stateSize; i++) {
			delete states[i];
		}
		delete []states;
		
		for (int i = N-1; i >= 0; i--) {
			if (top[i] > 0) {
				x = top[i] - 1;
				y = i;
				break;
			}
		}
	
	}

	/*
     //a naive example
	for (int i = N-1; i >= 0; i--) {
		if (top[i] > 0) {
			x = top[i] - 1;
			y = i;
			break;
		}
	}
	*/
	
	
	/*
		不要更改这段代码
	*/
	clearArray(M, N, board);
	return new Point(x, y);
}


/*
	getPoint函数返回的Point指针是在本dll模块中声明的，为避免产生堆错误，应在外部调用本dll中的
	函数来释放空间，而不应该在外部直接delete
*/
extern "C" __declspec(dllexport) void clearPoint(Point* p){
	delete p;
	return;
}

/*
	清除top和board数组
*/
void clearArray(int M, int N, int** board){
	for(int i = 0; i < M; i++){
		delete[] board[i];
	}
	delete[] board;
}


/*
	添加你自己的辅助函数，你可以声明自己的类、函数，添加新的.h .cpp文件来辅助实现你的想法
*/
