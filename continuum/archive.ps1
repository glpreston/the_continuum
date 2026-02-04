# Root of your project
$root = "E:\the_continuum\continuum"
$archiveRoot = "$root\archive"

# List of files to archive (relative paths)
$files = @(
    "actors\emotional_hooks.py",
    "actors\meta_persona_layer.py",
    "actors\specialist_actor.py",
    "actors\utils.py",

    "aira\logging.py",
    "aira\meta_rewrite.py",
    "aira\polish.py",
    "aira\safety.py",

    "persona\actor_cards.py",
    "persona\voiceprints.py",
    "persona\style_rewrite.py",
    "persona\voiceprint_loader.py",
    "persona\emotional_memory.py",
    "persona\meta_persona.py",

    "emotion\debug_panel.py",
    "emotion\emotional_momentum.py",
    "emotion\emotional_memory_influence.py",
    "emotion\emotional_memory_decay.py",
    "emotion\transition.py",

    "tools\registry.py",
    "tools\tool_registry.py",

    "db\models\user_memory.py",
    "db\models\user_preferences.py",
    "db\models\user_voiceprints.py",
    "db\models\users.py",
    "db\models\system_config.py",

    "db\mysql_connection.py",

    "orchestrator\fusion_smoothing.py",
    "orchestrator\jury_rubric.py",
    "orchestrator\legacy_items.py",
    "orchestrator\model_selector.py",
    "orchestrator\node_selector.py",
    "orchestrator\router\router.py",
    "orchestrator\controller_legacy.py",
    "orchestrator\model_registry.py",

    "orchestrator\router\tests\conftest.py",
    "orchestrator\router\tests\factories.py",
    "test\test_senate_phase4.py",

    "core\logging\decorators.py",
    "core\messages.py",
    "core\routing.py",
    "core\turn_logger.py",

    "websearch.py"
)

foreach ($file in $files) {
    $source = Join-Path $root $file
    if (Test-Path $source) {
        $dest = Join-Path $archiveRoot $file
        $destDir = Split-Path $dest

        # Create directory structure in archive
        if (!(Test-Path $destDir)) {
            New-Item -ItemType Directory -Path $destDir -Force | Out-Null
        }

        # Move the file
        Move-Item -Path $source -Destination $dest -Force
        Write-Host "Archived: $file"
    } else {
        Write-Host "Not found (skipped): $file"
    }
}