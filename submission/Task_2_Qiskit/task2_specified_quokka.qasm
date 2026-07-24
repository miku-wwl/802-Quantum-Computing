OPENQASM 2.0;

qreg q[2];
creg q0_out[1];
creg q1_out[1];
h q[0];
x q[1];
cx q[0],q[1];
measure q[0] -> q0_out[0];
measure q[1] -> q1_out[0];