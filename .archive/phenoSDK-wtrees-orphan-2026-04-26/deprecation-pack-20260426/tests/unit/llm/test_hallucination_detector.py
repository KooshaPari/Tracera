from pheno.llm.quality import BehaviourFlag, detect_behavioural_flags


def test_detects_confirmation_loop_after_user_approval() -> None:
    conversation = [
        {"role": "assistant", "content": "Would you like me to proceed with steps A, B, C?"},
        {"role": "user", "content": "Yes, please do."},
        {"role": "assistant", "content": "Great! Would you like me to proceed now?"},
    ]

    result = detect_behavioural_flags(conversation)
    assert BehaviourFlag.CONFIRMATION_LOOP in result.flags
    assert result.flags[BehaviourFlag.CONFIRMATION_LOOP] >= 0.4


def test_detects_repetitive_stall_pattern() -> None:
    conversation = [
        {"role": "assistant", "content": "Let me check the database."},
        {"role": "assistant", "content": "Let me check the database."},
        {"role": "assistant", "content": "Let me check the database again."},
        {"role": "assistant", "content": "Still checking..."},
    ]

    result = detect_behavioural_flags(conversation)
    assert BehaviourFlag.REPETITIVE_STALL in result.flags


def test_detects_random_hallucination_gibberish() -> None:
    conversation = [
        {"role": "assistant", "content": "ofhsdoghosighn the history of germany results in 🤯💥💥(((%%%%%%%#####@@@@@@@!!!!"}},
    ]

    result = detect_behavioural_flags(conversation)
    assert BehaviourFlag.RANDOM_HALLUCINATION in result.flags


def test_detects_tool_syntax_error() -> None:
    conversation = [
        {"role": "assistant", "content": "<x.ai:functioncall> check_weather </x.ai:functioncall>"},
    ]

    result = detect_behavioural_flags(conversation)
    assert BehaviourFlag.TOOL_SYNTAX_ERROR in result.flags
