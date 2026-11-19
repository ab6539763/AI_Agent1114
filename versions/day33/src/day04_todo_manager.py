"""
STARMIND-004 模块一：星辰智脑研发待办事项管理器（Todo CLI 引擎）。
演示 list 增删改查、tuple 不可变记录与解包、列表推导式过滤。
"""

from typing import List, Tuple

# 定义类型别名：单条任务为 (任务ID, 任务标题, 是否完成)
TaskRecord = Tuple[int, str, bool]


def add_task(tasks: List[TaskRecord], title: str) -> TaskRecord:
    """向任务列表末尾添加一条新待办，并返回新建的任务元组。"""
    cleaned = title.strip()
    if not cleaned:
        raise ValueError("任务标题不能为空")
    # 计算下一个自增 ID（即使中间删除过任务也不会冲突）
    next_id = max((t[0] for t in tasks), default=0) + 1
    record: TaskRecord = (next_id, cleaned, False)
    tasks.append(record)
    return record


def complete_task(tasks: List[TaskRecord], task_id: int) -> bool:
    """按任务 ID 将任务标记为已完成，成功返回 True，未找到返回 False。"""
    for idx, (tid, title, _done) in enumerate(tasks):
        if tid == task_id:
            # 元组不可变，因此构造新元组替换原位置元素
            tasks[idx] = (tid, title, True)
            return True
    return False


def remove_task(tasks: List[TaskRecord], task_id: int) -> bool:
    """安全删除指定 ID 的任务（避免遍历时原地 remove 引发错位）。"""
    original_len = len(tasks)
    # 使用切片赋值 tasks[:] 原地替换为推导式过滤后的新列表
    tasks[:] = [t for t in tasks if t[0] != task_id]
    return len(tasks) < original_len


def filter_tasks(tasks: List[TaskRecord], only_pending: bool = False) -> List[TaskRecord]:
    """根据完成状态筛选任务列表。"""
    if only_pending:
        return [t for t in tasks if not t[2]]
    return list(tasks)


def summarize_tasks(tasks: List[TaskRecord]) -> Tuple[int, int, int]:
    """返回只读统计快照：(总任务数, 已完成数, 待办数)。"""
    total = len(tasks)
    done_count = sum(1 for _, _, done in tasks if done)
    return (total, done_count, total - done_count)


if __name__ == "__main__":
    todo_list: List[TaskRecord] = []
    add_task(todo_list, "配置星辰智脑开发环境")
    add_task(todo_list, "完成客服文本清洗器")
    add_task(todo_list, "编写 Day 4 单元测试")
    complete_task(todo_list, 1)
    remove_task(todo_list, 2)

    total, done, pending = summarize_tasks(todo_list)
    print(f"任务概览 -> 总计:{total} | 已完成:{done} | 待办:{pending}")
    for tid, title, is_done in todo_list:
        mark = "[x]" if is_done else "[ ]"
        print(f"  {mark} #{tid} {title}")

