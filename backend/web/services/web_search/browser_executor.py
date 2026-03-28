import asyncio
import json
import os

os.environ.setdefault("BROWSER_USE_LOGGING_LEVEL", "warning")
os.environ.setdefault("ANONYMIZED_TELEMETRY", "false")

from browser_use import Agent, Browser, ChatOpenAI
from langchain_openai import ChatOpenAI as LangChainOpenAI

_browser = Browser()


def _build_browser_llm():
    api_key = os.getenv('API_KEY')
    base_url = os.getenv('API_BASE')
    model = os.getenv('MODEL')

    if not api_key:
        raise ValueError('缺少 API_KEY')
    if not base_url:
        raise ValueError('缺少 API_BASE')
    if not model:
        raise ValueError('缺少 MODEL')

    return ChatOpenAI(
        base_url=base_url,
        model=model,
        api_key=api_key,
        temperature=0.1,
    )


def _build_decompose_llm():
    api_key = os.getenv('API_KEY')
    base_url = os.getenv('API_BASE')

    if not api_key:
        raise ValueError('缺少 API_KEY')
    if not base_url:
        raise ValueError('缺少 API_BASE')

    return LangChainOpenAI(
        model='deepseek-ai/DeepSeek-V3',
        openai_api_key=api_key,
        openai_api_base=base_url,
        temperature=0.0,
    )


def _decompose_query(query: str) -> list[str]:
    """调用小模型把用户 query 拆解为 1~N 个子查询，返回列表。"""
    llm = _build_decompose_llm()
    prompt = f"""将下面的用户问题拆解为若干个独立的、适合直接搜索引擎搜索的子查询。
每个子查询单独一行，不带编号或符号前缀，不做任何解释。
如果问题本身已经足够简单无需拆解，只输出原问题一行即可。

用户问题：{query}"""

    response = llm.invoke(prompt)
    raw = response.content.strip()
    subqueries = [line.strip() for line in raw.splitlines() if line.strip()]
    if not subqueries:
        subqueries = [query]
    print('Query decomposed into %d subqueries: %s', len(subqueries), subqueries)
    return subqueries


def _build_search_answer_task(query: str) -> str:
    return f"""你是一个网页研究助手。请用最少的步骤完成以下搜索任务。

用户问题：
{query}

执行规则（严格遵守，不得多余操作）：
1. 打开 Baidu（https://www.baidu.com）并搜索该问题。
2. 如果搜索结果页面已直接显示答案，立即提取并调用 done 结束。不要再点击任何链接。
3. 仅当搜索结果页面没有直接答案时，才执行scroll / extract等操作寻找并点击最相关的一条结果。
4. 提取到答案后必须立刻调用 done，不得再执行任何 scroll / extract / click 操作。

输出格式（必须以"最终答案："开头）：
最终答案：
<中文简述>

关键点：
- <要点>

来源：
- <标题> | <URL>""".strip()


async def _run_browser_search_async(query: str) -> str:
    llm = _build_browser_llm()
    agent = Agent(
        task=_build_search_answer_task(query),
        llm=llm,
        browser=_browser,
        use_vision=os.getenv('USE_VISION', 'false').lower() == 'true',
        max_steps=int(os.getenv('MAX_STEPS', '30')),
    )
    result = await agent.run()
    return result.final_result() or ''


async def _run_all_searches_async(subqueries: list[str]) -> str:
    parts = []
    for i, q in enumerate(subqueries, 1):
        try:
            r = await _run_browser_search_async(q)
        except Exception as e:
            print('Warning: Subquery %d failed: %s' % (i, e))
            continue
        if r:
            if len(subqueries) > 1:
                parts.append(f'【子查询 {i}：{q}】\n{r}')
            else:
                parts.append(r)

    return '\n\n'.join(parts)


def run_browser_search(query: str) -> str:
    subqueries = _decompose_query(query)
    return asyncio.run(_run_all_searches_async(subqueries))
