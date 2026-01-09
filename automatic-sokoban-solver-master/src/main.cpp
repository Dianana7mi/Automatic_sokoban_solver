#include <cstdio>
#include <iostream>
#include <fstream>
#include <string>
#include <limits>
#include <algorithm>
#ifdef _WIN32
#include <windows.h>
#endif
#include "game_solver.h"
#include "draw.h"

using namespace std;

void read_file(int& mm, int& nn, string& temp, const string& filename = "box.txt"){
    mm=0;
    nn=0;
    temp.clear();
    ifstream file_read;
    file_read.open(filename,ios::in);

    if (!file_read) {
        cout << filename << " 文件不存在！" << endl;
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

int main(int argc, char* argv[]) {
#ifdef _WIN32
    SetConsoleOutputCP(65001);
#endif
    int mm;
    int nn;
    string temp;
    
    if (argc > 1) {
        int algo = 0;
        int mem = 100;
        string filename = "box.txt";
        
        if (argc >= 2) algo = std::stoi(argv[1]);
        if (argc >= 3) mem = std::stoi(argv[2]);
        if (argc >= 4) filename = argv[3];
        
        read_file(mm, nn, temp, filename);
        game_solver ga(temp, mm, nn, mem);
        auto ss = ga.test_template(algo);
        
        draw_picture d;
        auto full_path = d.get_complete(ss);
        std::reverse(full_path.begin(), full_path.end());
        
        std::cout << "---JSON_START---" << std::endl;
        std::cout << "[" << std::endl;
        for (size_t k = 0; k < full_path.size(); ++k) {
             auto mat = full_path[k].get_matrix2();
             std::cout << "  [" << std::endl;
             for (size_t r = 0; r < mat.size(); ++r) {
                 std::cout << "    [";
                 for (size_t c_idx = 0; c_idx < mat[r].size(); ++c_idx) {
                     std::cout << (int)mat[r][c_idx];
                     if (c_idx < mat[r].size() - 1) std::cout << ", ";
                 }
                 std::cout << "]";
                 if (r < mat.size() - 1) std::cout << ",";
                 std::cout << std::endl;
             }
             std::cout << "  ]";
             if (k < full_path.size() - 1) std::cout << ",";
             std::cout << std::endl;
        }
        std::cout << "]" << std::endl;
        std::cout << "---JSON_END---" << std::endl;
        return 0;
    }

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
