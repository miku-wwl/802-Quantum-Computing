# MSE802 Assessment 2：材料与本地环境分析

## 结论

作业要求四个独立任务，最终以 ZIP 提交，每个任务放在独立目录中。代码应使用
Jupyter Notebook（或 Google Colab），并使用清晰的标题、图、公式、结果和一致的
APA/IEEE 引用。

课程资料已经位于 `MSE802 Quantum Computing/`。PDF 中写的文件名与实际文件名不同，
实际 starter notebooks 是：

- `Week-12/AS2_Files/AS2_Files/Quantum_Tic_Tac_Toe__AS2.ipynb`
- `Week-12/AS2_Files/AS2_Files/Quantum_ML_AS2.ipynb`

两份 notebook 均已核对。Task 4 没有 TensorFlow/PyTorch 依赖；它用 OpenQASM 2
字符串、Quokka REST 请求、NumPy/SciPy 优化和 Matplotlib。Task 3 使用
`google.colab.widgets.Grid`，不能原样在本地 Jupyter 运行，需要在完成代码时迁移到
原生 `ipywidgets` 布局。

## 各任务需要的课程材料

### Task 1：Entanglement Demonstrations（25%）

需要：

- `Week-3/Week-3/statevector_probability_amplitudes_ket_bra_notation (1).ipynb`
  （statevector、Bell state、概率、tensor product）
- `Week-6/quantum_gates_tutorial.ipynb`
  （H、CNOT、Bell-state circuit、Aer measurement）
- `Week-7/Scripts/Cirq_Gates.ipynb`（Cirq gate 与 simulator）
- `Week-10/Quantum_Teleportation_Teaching (1).ipynb`
  （Bell states、H + CNOT 与纠缠的深入解释）
- Hadamard 与 CNOT/CX gate、测量、shots 与 histogram 的材料
- Cirq 的 circuit、simulator、measurement 示例
- `Week-7/Scripts/quokka_access (1) (1).ipynb`
  （Qiskit QASM 2 导出和 Quokka REST 请求）

工作内容：

- 用 Cirq 构造 `( |00> + |11> ) / sqrt(2)`
- 先在本地模拟器验证，再在 Quokka 执行
- 展示电路、采样计数/概率，并解释为什么理想结果只包含 `00` 和 `11`

### Task 2：Qiskit circuits（35%）

需要：

- `Week-6/quantum_gates_tutorial.ipynb`
  （Qiskit H/X/CNOT、measurement、statevector）
- `Week-7/Scripts/quokka_access (1) (1).ipynb`
  （OpenQASM 2 导入/导出、Quokka payload 和结果解析）
- `Week-7/Scripts/Cirq_Gates.ipynb`（自定义 circuit 的 gate 选择参考）
- 对 PDF 第 4 页中 `C` 方块确切含义的课堂说明；图示不像标准 Qiskit gate
  notation，不应在没有课程上下文时擅自认定

工作内容：

- 重建指定电路并在 Quokka 测量
- 自行设计使用不同 qubit 和多种 gate 的 OpenQASM circuit
- 本地 Aer 验证后提交 Quokka，保存输出

### Task 3：Investigate a quantum code（25%）

主要材料：

- `Week-12/AS2_Files/AS2_Files/Quantum_Tic_Tac_Toe__AS2.ipynb`
- `Week-6/quantum_gates_tutorial.ipynb`
- `Week-7/Scripts/Cirq_Gates.ipynb`

还需要：

- 量子 gate、受控 gate、电路生成与 measurement 的课程材料
- 多次游戏运行记录、生成的电路和结果

交付：

- 补全后的 notebook
- Word 报告：目的、代码结构、玩法、游戏如何生成电路、所用 gates 的性质与作用

### Task 4：Machine Learning Quantum Analysis（15%）

主要材料：

- `Week-12/AS2_Files/AS2_Files/Quantum_ML_AS2.ipynb`
- `Week-7/Scripts/quokka_access (1) (1).ipynb`

数据由 notebook 内的 `generate_data()` 生成，不需要外部图片文件。电路把每个 2x2
二值图像展开为 4 bits，以 `x` gates 做 basis encoding，再使用递归配对的 `ry + ry
+ cx` blocks，最后测量最后一个 qubit。优化使用 SciPy Nelder-Mead 和自写 SPSA。

还需要：

- image encoding / feature map / parameterised quantum circuit 的材料
- 经典基线与公平性能比较的材料

交付：

- 标出电路输入数据和输入代码位置，并解释量子部分（不分析优化算法）
- 记录每次 iteration 的 metric 和耗时，绘制两张图
- 去除量子电脑/量子电路的本地经典版本
- 比较效率（时间/资源）和效果（metric/accuracy）
- 修改后的 notebook 和 Word 报告

## 已配置的本地工作环境

- 项目私有 Python 3.11 环境（`.venv`）
- JupyterLab / ipykernel / ipywidgets
- Cirq
- Qiskit、Qiskit Aer、Qiskit Machine Learning
- NumPy、SciPy、pandas、scikit-learn
- Matplotlib、Seaborn、Pillow
- Requests（用于课程提供的 Quokka REST/QASM 接口）
- SymPy（Task 4 starter notebook 的直接依赖）
- python-docx（报告辅助生成）

Python 3.11 是有意选择：它满足当前 Cirq，并通常比系统 Python 3.13 更容易兼容课程
中较早编写的 notebook。精确版本由 `uv.lock` 固定。

## 使用方法（PowerShell）

首次或依赖变更后：

```powershell
uv sync
uv run python scripts/verify_environment.py
```

启动 JupyterLab：

```powershell
uv run jupyter lab
```

在 VS Code 中选择解释器：

```text
.venv\Scripts\python.exe
```

## Quokka 接入

本地环境可以验证 Cirq、Qiskit Aer 和 OpenQASM 2，但不能替代 rubric 明确要求的
Quokka 执行。课程 notebook 使用
`https://quokka1.quokkacomputing.com/qsim/qasm`（原代码为 HTTP，会重定向到
HTTPS）。2026-07-24 已确认主机可解析、80/443 可连接，HTTPS 路径有响应；尚未发送
POST 作业。正式执行前仍应向导师确认 endpoint、可用时间和使用规则。

本机已根据 `.env.example` 创建被 Git 忽略的 `.env`。如果导师变更 endpoint，请只
修改本机 `.env`。不要把私有设备地址、token 或凭据提交到仓库。

## 建议提交目录

```text
assessment2/
  task1_entanglement/
  task2_qiskit/
  task3_tic_tac_toe/
  task4_ml_quantum/
```

每个目录保存对应 notebook、报告、图和必要结果。最终压缩 `assessment2`，不要把
`.venv`、缓存、凭据或临时文件放进 ZIP。

## 尚未满足的外部条件与代码迁移

1. Quokka endpoint 虽可达，但正式 POST 执行权限、设备可用时间和规则仍需导师确认。
2. Task 3 starter notebook 的 Colab-only Grid UI 需要迁移到本地 `ipywidgets`。
3. Task 3 有明确未完成代码：Not/O/X/SWAP gate 操作和 8 组胜利条件。
4. Task 4 需要增加 iteration metric/time 记录、绘图和无量子电路的经典基线。
5. PDF Task 2 中 `C` 方块的确切语义需要课堂上下文或导师确认。
