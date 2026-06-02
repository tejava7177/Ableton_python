cmake_minimum_required(VERSION 3.22)

project(ChordFlowWorkstation VERSION 0.1.0 LANGUAGES C CXX)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)

# Prefer an existing local JUCE checkout if one is added later.
set(JUCE_SOURCE_DIR "" CACHE PATH "Path to a JUCE source checkout")

if (EXISTS "${CMAKE_CURRENT_SOURCE_DIR}/JUCE/CMakeLists.txt")
    add_subdirectory(JUCE)
elseif (JUCE_SOURCE_DIR AND EXISTS "${JUCE_SOURCE_DIR}/CMakeLists.txt")
    add_subdirectory("${JUCE_SOURCE_DIR}" JUCE)
else()
    find_package(JUCE CONFIG QUIET)
endif()

if (NOT TARGET juce::juce_gui_extra)
    message(FATAL_ERROR
        "JUCE was not found.\n"
        "Add JUCE as a subdirectory at ChordFlowWorkstation/JUCE, configure CMake with -DJUCE_SOURCE_DIR=/path/to/JUCE,\n"
        "or provide a JUCE package config with -DJUCE_DIR=/path/to/JUCEConfig.cmake parent.\n"
        "TODO: wire this project to the team's preferred JUCE dependency source once available."
    )
endif()

juce_add_gui_app(ChordFlowWorkstation
    PRODUCT_NAME "ChordFlow Workstation"
    COMPANY_NAME "ChordFlow"
)

target_sources(ChordFlowWorkstation
    PRIVATE
        Source/Main.cpp
        Source/MainComponent.cpp
        Source/UI/BackingSummaryComponent.cpp
        Source/UI/ChordInputComponent.cpp
        Source/UI/SectionPanelComponent.cpp
        Source/UI/GrooveControlComponent.cpp
        Source/UI/TransportComponent.cpp
)

target_include_directories(ChordFlowWorkstation
    PRIVATE
        Source
)

target_compile_definitions(ChordFlowWorkstation
    PRIVATE
        JUCE_WEB_BROWSER=0
        JUCE_USE_CURL=0
)

target_link_libraries(ChordFlowWorkstation
    PRIVATE
        juce::juce_gui_extra
    PUBLIC
        juce::juce_recommended_config_flags
        juce::juce_recommended_warning_flags
)
