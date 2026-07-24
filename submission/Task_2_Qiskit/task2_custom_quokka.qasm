OPENQASM 2.0;

qreg q[3];
creg q0_out[1];
creg q1_out[1];
creg q2_out[1];
h q[0];
ry(1.0471975511965976) q[1];
x q[2];
cx q[0],q[1];
rz(0.7853981633974483) q[1];
h q[1];
cx q[1],q[2];
measure q[0] -> q0_out[0];
measure q[1] -> q1_out[0];
measure q[2] -> q2_out[0];
