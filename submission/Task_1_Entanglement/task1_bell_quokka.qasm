// Generated from Cirq v1.7.0

OPENQASM 2.0;



// Qubits: [q(0), q(1)]
qreg q[2];
creg q0_out[1];
creg q1_out[1];


h q[0];
cx q[0],q[1];

// Gate: cirq.MeasurementGate(2, cirq.MeasurementKey(name='bell'), ())
measure q[0] -> q0_out[0];
measure q[1] -> q1_out[0];
