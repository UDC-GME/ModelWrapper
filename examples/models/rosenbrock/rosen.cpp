/* 
 * Reads the values from a yaml file and * returns the value of the
 * rosenbrock  function evaluated at those points in json format
 *
 */

#include <iostream>
#include <cmath>
#include <fstream>

#include <yaml-cpp/yaml.h>
#include <json/json.h>

using std::pow;

double rosen(const double x1, const double x2)
{
    return 100*pow((x2 - pow(x1,2)),2) + pow(1-x1,2);
}

double circle(const double x1, const double x2)
{
    return pow(x1,2) + pow(x2,2) - 1;
}

int main()
{
    YAML::Node params = YAML::LoadFile("parameters.yaml");
    const double x1 = params["x1"].as<double>();
    const double x2 = params["x2"].as<double>();

    Json::Value results;
    results["f"] = rosen(x1, x2);
    results["g"] = circle(x1, x2);

    std::ofstream resultFile;
    resultFile.open("results.json");
    resultFile << results;
    resultFile.close();

    return 0;
}

