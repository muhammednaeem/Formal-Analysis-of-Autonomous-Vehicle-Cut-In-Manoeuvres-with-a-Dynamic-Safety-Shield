#include <cstdint>
#include <fstream>

extern "C" int32_t WriteVar(
    double var1,
    double var2,
    double var3,
    double var4,
    double var5,
    double var6,
    double var7,
    double var8,
    double var9,
    double var10,
    double var11,
    double var12,
    double var13,
    double var14,
    double var15)
{
    const char* outputPath =
        "./TextFiles/clock_values.txt";

    std::ofstream output(
        outputPath,
        std::ios::out | std::ios::app
    );

    if (!output.is_open()) {
        return -1;
    }

    output
        << var1 << " "
        << var2 << " "
        << var3 << " "
        << var4 << " "
        << var5 << " "
        << var6 << " "
        << var7 << " "
        << var8 << " "
        << var9 << " "
        << var10 << " "
        << var11 << " "
        << var12 << " "
        << var13 << " "
        << var14 << " "
        << var15 << '\n';

    output.flush();

    if (!output.good()) {
        return -2;
    }

    output.close();
    return 1;
}