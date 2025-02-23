# Robot Order Automation

This project automates ordering robots from RobotSpareBin Industries using the [Robocorp Python framework](https://github.com/robocorp/robocorp). It processes orders from a CSV file, generates PDF receipts with embedded screenshots, and archives them into a ZIP file.

## Features
- Opens the RobotSpareBin website and handles the initial popup.
- Downloads `orders.csv` dynamically from [here](https://robotsparebinindustries.com/orders.csv).
- Fills and submits order forms for each row in the CSV.
- Saves each receipt as a PDF with a robot screenshot.
- Creates a `receipts.zip` archive in the `output/` folder.
- Cleans up temporary files.

## Running the Robot

### Prerequisites
- Python 3.9+ (specified in `robot.yaml`).
- Robocorp libraries (installed via `robot.yaml` dependencies).

### VS Code
1. Install the [Robocorp Code](https://robocorp.com/docs/developer-tools/visual-studio-code/extension-features) extension for VS Code.
2. Use the side panel or command palette to run the task `order_robot_from_RobotSpareBin`.

### Command Line
1. Install [RCC](https://github.com/robocorp/rcc?tab=readme-ov-file#getting-started).
2. Run:
   ```bash
   rcc run
   ```
   Alternatively, use:
   ```bash
   python -m robocorp.tasks run tasks.py --task order_robot_from_RobotSpareBin
   ```

## Results
- After running, find `receipts.zip` in the `output/` folder.
- Check `log.html` in `output/` for execution details.

## Project Structure
```
tasks.py        # Main script with the robot logic
robot.yaml      # Configuration file specifying dependencies and task execution
.gitignore      # Excludes generated files (output/, orders.csv, etc.)
README.md       # This documentation
LICENSE         # Project license (optional)
```

## Dependencies
Dependencies are managed in `robot.yaml`:
```yaml
dependencies:
  - rpaframework==11.0.0
  - robocorp-browser==2.0.0
```
No manual `pip install` needed; RCC handles this based on `robot.yaml`.

## Setup Notes
- The robot runs out-of-the-box when cloned from GitHub.
- No manual setup required; `orders.csv` is downloaded during execution.
- Tested for Robocorp’s automated verification.

## Next Steps
- Explore [Robocorp Documentation](https://robocorp.com/docs) for more RPA insights.
- Try [Robocorp ReMark](https://robocorp.com/remark) for AI-assisted coding.
- Check the [Portal](https://portal.robocorp.com/) for additional examples.

## Repository
GitHub: [robot-order-automation](https://github.com/parajulitilak/robot-order-automation)

Submitted for Robocorp Python Certification quiz evaluation.

