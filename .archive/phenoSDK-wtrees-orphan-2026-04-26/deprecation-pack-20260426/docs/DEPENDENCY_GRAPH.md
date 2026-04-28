# Dependency Graph (Mermaid)

This graph shows kit-to-dependency relationships for dependencies used by at least 3 kits.

```mermaid
graph LR
  %% Kits
  subgraph Kits
    kit_kinfra["KInfra"]
    kit_adapter_kit["adapter-kit"]
    kit_api_gateway_kit["api-gateway-kit"]
    kit_authkit_client["pheno.auth"]
    kit_build_analyzer_kit["build-analyzer-kit"]
    kit_cli_builder_kit["cli-builder-kit"]
    kit_config_kit["config-kit"]
    kit_db_kit["db-kit"]
    kit_deploy_kit["deploy-kit"]
    kit_domain_kit["domain-kit"]
    kit_event_kit["event-kit"]
    kit_filewatch_kit["filewatch-kit"]
    kit_grpc_kit["grpc-kit"]
    kit_mcp_qa["pheno.mcp.qa"]
    kit_mcp_infra_sdk["mcp-infra-sdk"]
    kit_mcp_sdk_kit["mcp-sdk-kit"]
    kit_multi_cloud_deploy_kit["multi-cloud-deploy-kit"]
    kit_observability_kit["observability-kit"]
    kit_orchestrator_kit["orchestrator-kit"]
    kit_pheno_cli["pheno_cli"]
    kit_process_monitor_sdk["process-monitor-sdk"]
    kit_pydevkit["pydevkit"]
    kit_resource_management_kit["resource-management-kit"]
    kit_storage_kit["storage-kit"]
    kit_stream_kit["stream-kit"]
    kit_test_kit["test-kit"]
    kit_tui_kit["tui-kit"]
    kit_vector_kit["vector-kit"]
    kit_workflow_kit["workflow-kit"]
  end
  %% Dependencies (top)
  subgraph Deps_≥3
    dep_pydantic["pydantic"]
    dep_python_dotenv["python-dotenv"]
    dep_httpx["httpx"]
    dep_pytest["pytest"]
    dep_pytest_asyncio["pytest-asyncio"]
    dep_rich["rich"]
    dep_pyyaml["pyyaml"]
    dep_aiohttp["aiohttp"]
    dep_textual["textual"]
    dep_pytest_cov["pytest-cov"]
    dep_black["black"]
    dep_mypy["mypy"]
  end
  %% Edges
  kit_pydevkit --> dep_pydantic
  kit_pydevkit --> dep_python_dotenv
  kit_pydevkit --> dep_httpx
  kit_process_monitor_sdk --> dep_pydantic
  kit_process_monitor_sdk --> dep_python_dotenv
  kit_authkit_client --> dep_pydantic
  kit_authkit_client --> dep_python_dotenv
  kit_authkit_client --> dep_httpx
  kit_workflow_kit --> dep_pydantic
  kit_workflow_kit --> dep_python_dotenv
  kit_api_gateway_kit --> dep_pydantic
  kit_api_gateway_kit --> dep_python_dotenv
  kit_pheno_cli --> dep_rich
  kit_pheno_cli --> dep_textual
  kit_pheno_cli --> dep_pydantic
  kit_pheno_cli --> dep_pyyaml
  kit_pheno_cli --> dep_httpx
  kit_pheno_cli --> dep_python_dotenv
  kit_storage_kit --> dep_pydantic
  kit_storage_kit --> dep_python_dotenv
  kit_adapter_kit --> dep_pydantic
  kit_adapter_kit --> dep_python_dotenv
  kit_adapter_kit --> dep_pytest
  kit_adapter_kit --> dep_pytest_asyncio
  kit_adapter_kit --> dep_pytest_cov
  kit_db_kit --> dep_pydantic
  kit_db_kit --> dep_python_dotenv
  kit_build_analyzer_kit --> dep_pydantic
  kit_build_analyzer_kit --> dep_python_dotenv
  kit_test_kit --> dep_pytest
  kit_test_kit --> dep_pytest_asyncio
  kit_test_kit --> dep_pytest_cov
  kit_test_kit --> dep_httpx
  kit_test_kit --> dep_aiohttp
  kit_test_kit --> dep_pydantic
  kit_tui_kit --> dep_textual
  kit_tui_kit --> dep_rich
  kit_tui_kit --> dep_pydantic
  kit_stream_kit --> dep_pydantic
  kit_stream_kit --> dep_python_dotenv
  kit_stream_kit --> dep_aiohttp
  kit_stream_kit --> dep_pytest
  kit_stream_kit --> dep_pytest_asyncio
  kit_stream_kit --> dep_black
  kit_stream_kit --> dep_mypy
  kit_config_kit --> dep_pydantic
  kit_config_kit --> dep_python_dotenv
  kit_orchestrator_kit --> dep_pydantic
  kit_orchestrator_kit --> dep_python_dotenv
  kit_mcp_qa --> dep_pytest
  kit_mcp_qa --> dep_pytest_asyncio
  kit_mcp_qa --> dep_aiohttp
  kit_mcp_qa --> dep_httpx
  kit_mcp_qa --> dep_pydantic
  kit_mcp_qa --> dep_textual
  kit_mcp_qa --> dep_rich
  kit_cli_builder_kit --> dep_pydantic
  kit_cli_builder_kit --> dep_python_dotenv
  kit_vector_kit --> dep_pydantic
  kit_vector_kit --> dep_python_dotenv
  kit_filewatch_kit --> dep_pydantic
  kit_filewatch_kit --> dep_python_dotenv
  kit_filewatch_kit --> dep_pytest
  kit_filewatch_kit --> dep_pytest_asyncio
  kit_filewatch_kit --> dep_black
  kit_filewatch_kit --> dep_mypy
  kit_mcp_sdk_kit --> dep_pydantic
  kit_mcp_sdk_kit --> dep_python_dotenv
  kit_deploy_kit --> dep_pydantic
  kit_deploy_kit --> dep_python_dotenv
  kit_observability_kit --> dep_pydantic
  kit_observability_kit --> dep_python_dotenv
  kit_multi_cloud_deploy_kit --> dep_pydantic
  kit_multi_cloud_deploy_kit --> dep_python_dotenv
  kit_event_kit --> dep_pydantic
  kit_event_kit --> dep_python_dotenv
  kit_event_kit --> dep_httpx
  kit_mcp_infra_sdk --> dep_pydantic
  kit_mcp_infra_sdk --> dep_python_dotenv
  kit_resource_management_kit --> dep_pydantic
  kit_resource_management_kit --> dep_python_dotenv
  kit_domain_kit --> dep_pydantic
  kit_domain_kit --> dep_python_dotenv
  kit_kinfra --> dep_aiohttp
  kit_kinfra --> dep_pyyaml
  kit_kinfra --> dep_rich
  kit_kinfra --> dep_pydantic
  kit_kinfra --> dep_pytest
  kit_kinfra --> dep_pytest_asyncio
  kit_kinfra --> dep_pytest_cov
  kit_kinfra --> dep_black
  kit_kinfra --> dep_mypy
```
