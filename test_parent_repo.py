#!/usr/bin/env python3
"""
Test script for parent repo display feature.
Tests only forked repositories to validate parent repo display.
"""
from gh_profile_repo_pins.repo_pins_exceptions import RepoPinImageThemeError
from gh_profile_repo_pins.repo_pins_generate import GenerateRepoPins
from gh_profile_repo_pins.repo_pins_img_data import RepoPinImgData
from gh_profile_repo_pins.repo_pins_img_svg import RepoPinImg
from gh_profile_repo_pins.utils import write_svg
import gh_profile_repo_pins.repo_pins_enum as enums


def test_parent_repo_display() -> None:
    """Test parent repo display for forked repositories only."""
    # Update themes first to load all available themes from themes.json
    GenerateRepoPins.update_themes()
    
    test_cases = [
        {
            "name": "test-parent-repo-short",
            "description": "Forked repository with short parent name",
            "data": {
                "name": "my-forked-repo",
                "stargazerCount": 150,
                "forkCount": 20,
                "owner": {"login": "testuser"},
                "description": "This is a test forked repository with a short parent repo name.",
                "url": "https://github.com/testuser/my-forked-repo",
                "primaryLanguage": {"name": "Python", "color": "#3572A5"},
                "isFork": True,
                "parent": {"nameWithOwner": "original-owner/original-repo"},
                "isTemplate": False,
                "isArchived": False,
            },
            "theme": "github_soft",
            "output_file": "test-fork-short-parent",
        },
        {
            "name": "test-parent-repo-long",
            "description": "Forked repository with long parent name",
            "data": {
                "name": "another-fork",
                "stargazerCount": 5000,
                "forkCount": 300,
                "owner": {"login": "testuser"},
                "description": "Testing with a very long parent repository name to test truncation.",
                "url": "https://github.com/testuser/another-fork",
                "primaryLanguage": {"name": "TypeScript", "color": "#3178C6"},
                "isFork": True,
                "parent": {"nameWithOwner": "very-long-organization-name/very-long-repository-name-with-many-words"},
                "isTemplate": False,
                "isArchived": False,
            },
            "theme": "github",
            "output_file": "test-fork-long-parent",
        },
        {
            "name": "test-parent-repo-dracula",
            "description": "Forked repository with Dracula theme",
            "data": {
                "name": "dracula-fork",
                "stargazerCount": 42,
                "forkCount": 7,
                "owner": {"login": "testuser"},
                "description": "Testing parent repo display with Dracula theme.",
                "url": "https://github.com/testuser/dracula-fork",
                "primaryLanguage": {"name": "JavaScript", "color": "#F1E05A"},
                "isFork": True,
                "parent": {"nameWithOwner": "microsoft/vscode"},
                "isTemplate": False,
                "isArchived": False,
            },
            "theme": "dracula",
            "output_file": "test-fork-dracula",
        },
        {
            "name": "test-fork-with-description",
            "description": "Fork with description to test layout adjustment",
            "data": {
                "name": "repo-with-description",
                "stargazerCount": 1000,
                "forkCount": 50,
                "owner": {"login": "testuser"},
                "description": "This is a longer description to test that the parent repo display properly adjusts the description position. Lorem ipsum dolor sit amet, consectetur adipiscing elit.",
                "url": "https://github.com/testuser/repo-with-description",
                "primaryLanguage": {"name": "Rust", "color": "#DEA584"},
                "isFork": True,
                "parent": {"nameWithOwner": "rust-lang/rust"},
                "isTemplate": False,
                "isArchived": False,
            },
            "theme": "github_soft",
            "output_file": "test-fork-with-description",
        },
    ]
    
    print("Testing parent repo display feature...")
    print(f"Running {len(test_cases)} test cases\n")
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"[{i}/{len(test_cases)}] {test_case['description']}")
        
        try:
            # Convert theme string to enum - use the same pattern as existing test
            theme_enum = enums.RepoPinsImgThemeName(test_case["theme"])
            
            repo_pin = RepoPinImgData.format_repo_pin_data(
                repo_data=test_case["data"],
                username="testuser",
                theme_name=theme_enum,
            )
            
            # Verify it's a fork with parent
            assert repo_pin.is_fork, f"Test case {i}: Repository should be marked as fork"
            assert repo_pin.parent, f"Test case {i}: Repository should have parent"
            
            repo_pin_img = RepoPinImg(repo_pin_data=repo_pin)
            repo_pin_img.render()
            write_svg(svg_obj_str=repo_pin_img.svg, file_name=test_case["output_file"])
            
            print(f"  ✓ Generated: files/{test_case['output_file']}.svg")
            print(f"    Parent: {repo_pin.parent}")
            print()
            
        except ValueError as e:
            print(f"  ✗ Error: Theme validation failed - {e}\n")
        except RepoPinImageThemeError as e:
            print(f"  ✗ Error: {e.msg}\n")
        except Exception as e:
            print(f"  ✗ Error: {type(e).__name__}: {e}\n")
    
    print("Test completed! Check the 'files/' directory for generated SVG files.")
    print("Open the SVG files in a browser to visually verify the parent repo display.")


if __name__ == "__main__":
    test_parent_repo_display()

