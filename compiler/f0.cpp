#include <iostream>
#include <vector> 

using namespace std;

int main() {

    auto value = 17;
    auto gt = [](int value) { 
        auto gt_arg =  [value]( int arg ) {  return arg > value; };
        return gt_arg;
    }; 

    auto gt_17 = gt(17);

    vector<int> a = {1,2,3};

    for( auto i : a ) {
        cout << i << endl;
    }


    cout << "Hello\n";
      
    return 17;

}