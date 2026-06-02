#pragma once

#include <juce_core/juce_core.h>

struct Chord
{
    juce::String symbol;
    juce::String root;
    juce::String quality;
    int midiRoot = 60;
};
