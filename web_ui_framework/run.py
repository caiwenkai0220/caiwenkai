import os
import pytest


def run():
    # 定义目录路径（清晰区分不同文件类型）
    base_dir = os.path.dirname(__file__)
    reports_dir = os.path.join(base_dir, "reports")  # 存放最终报告（allure/html）
    allure_results_dir = os.path.join(reports_dir, "allure-results")  # Allure原始结果（JSON）
    pytest_html_report = os.path.join(reports_dir, "pytest_report.html")  # pytest-html报告

    # 确保目录存在
    os.makedirs(allure_results_dir, exist_ok=True)
    os.makedirs(os.path.dirname(pytest_html_report), exist_ok=True)  # 确保reports_dir存在

    # pytest 命令参数（修正路径和目录分工）
    args = [
        "tests/",  # 用例目录
        "-v",  # 详细输出
        "-s",  # 显示打印信息
        "--alluredir", allure_results_dir,  # 正确：Allure原始结果目录
        "--html", pytest_html_report,  # 正确：pytest-html报告路径（放在reports_dir下）
        "--self-contained-html",  # 将CSS嵌入HTML，不生成外部文件
        # "-k", "test_login",  # 可选：筛选用例
    ]

    # 执行用例
    pytest.main(args)

    # 生成 Allure 最终报告（从allure_results_dir读取原始数据）
    allure_report_dir = os.path.join(reports_dir, "allure-report")  # Allure HTML报告目录
    os.system(f"allure generate {allure_results_dir} -o {allure_report_dir} --clean")
    print(f"Allure报告已生成：{allure_report_dir}")
    print(f"pytest-html报告已生成：{pytest_html_report}")


if __name__ == "__main__":
    run()