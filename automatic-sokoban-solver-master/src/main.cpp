#include <cstdio>
#include <iostream>
#include <fstream>
#include <string>
#include <limits>
#ifdef _WIN32
#include <windows.h>
#endif
#include "game_solver.h"
#include "draw.h"

using namespace std;

void read_file(int& mm, int& nn, string& temp){
    mm=0;
    nn=0;
    temp.clear();
    ifstream file_read;
    file_read.open("box.txt",ios::in);

    if (!file_read) {
        printf("box.txt 文件不存在！\n");
#ifdef _WIN32
        system("pause");
#endif
        exit(100);
    }

    string x;
    string tempr;
    while (getline(file_read,x)) {
        tempr += x;
        mm += 1;
    }
    for(auto &tc: tempr){
        if(tc != '\r' && tc != '\n'){
            temp.push_back(tc);
        }
    }
    
    nn = temp.size() / mm;
    file_read.close();
}

int main() {
#ifdef _WIN32
    SetConsoleOutputCP(65001);
#endif
    int mm;
    int nn;
    string temp;
    read_file(mm,nn,temp);
    
    printf("请选择你的算法（输入 0, 1 或 2）\n");
    printf("0: A*算法;    1: DFS算法;    2: BFS算法\n");
    char input;
    int iinput;
    std::cin >> input;
    std::cin.ignore(std::numeric_limits<std::streamsize>::max(), '\n');
    if (input == '0' || input == '1' || input == '2') {
        iinput = input - '0'; // 将字符转换为对应的整数
    }
    else {
        printf("输入错误！\n");
        exit(-1);
    }

    printf("请输入你想要使用的内存大小（单位：MB）\n");
    int memval;
    std::cin >> memval;
    std::cin.ignore(std::numeric_limits<std::streamsize>::max(), '\n');

    game_solver ga(temp, mm, nn, memval);

    auto ss = ga.test_template(iinput);

    printf("按回车键查看解决方案\n");

    cin.get();
    draw_picture d;
    d.draw(ss);
}
