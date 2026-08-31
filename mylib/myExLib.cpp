#include <cstdint>
#include <fstream>

extern "C" int32_t WriteVar(
    double T,
    double X_Ego,
    double Y_Ego,
    double X_rear,
    double Y_rear,
    double X_slow,
    double Y_slow,
    double S_front_left_x,
    double S_front_left_y,
    double S_front_right_x,
    double S_front_right_y,
    double S_rear_right_x,
    double S_rear_right_y,
    double S_rear_left_x,
    double S_rear_left_y,
    double IS_front_left_x,
    double IS_front_left_y,
    double IS_front_right_x,
    double IS_front_right_y,
    double IS_rear_right_x,
    double IS_rear_right_y,
    double IS_rear_left_x,
    double IS_rear_left_y
)
{
    const char* outputPath =
        "/Users/mnm01/UPPAAL_Model_cutin/TextFiles/clock_values.txt";

    std::ofstream output(outputPath, std::ios::out | std::ios::app);

    if (!output.is_open()) {
        return -1;
    }

    output
        << T << " "
        << X_Ego << " "
        << Y_Ego << " "
        << X_rear << " "
        << Y_rear << " "
        << X_slow << " "
        << Y_slow << " "
        << S_front_left_x << " "
        << S_front_left_y << " "
        << S_front_right_x << " "
        << S_front_right_y << " "
        << S_rear_right_x << " "
        << S_rear_right_y << " "
        << S_rear_left_x << " "
        << S_rear_left_y << " "
        << IS_front_left_x << " "
        << IS_front_left_y << " "
        << IS_front_right_x << " "
        << IS_front_right_y << " "
        << IS_rear_right_x << " "
        << IS_rear_right_y << " "
        << IS_rear_left_x << " "
        << IS_rear_left_y << '\n';

    output.flush();

    if (!output.good()) {
        return -2;
    }

    return 1;
}
