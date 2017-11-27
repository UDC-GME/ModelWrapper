L = {{L}};

Point(1) = {0, 0, 0, 1};
Point(2) = {L, 0, 0, 1};
Point(3) = {2*L, 0, 0, 1};
Point(4) = {L, -L, 0, 1};

Line(1) = {1, 4};
Line(2) = {2, 4};
Line(3) = {3, 4};

// Number of elements
Transfinite Line {1,2,3} = 1;

Physical Point("Fix") = {1, 2, 3};
Physical Point("Load") = {4};
Physical Line("Bars") = {1, 2, 3};
Physical Line("Bar1") = {1, 3};
Physical Line("Bar2") = {2};
