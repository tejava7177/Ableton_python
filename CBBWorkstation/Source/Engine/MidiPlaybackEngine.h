#pragma once

#include <juce_events/juce_events.h>

namespace Engine
{
class MidiPlaybackEngine
{
public:
    MidiPlaybackEngine() = default;

    void play(const juce::String& playbackSummary, bool shouldLoop)
    {
        playing = true;
        loopEnabled = shouldLoop;
        currentSummary = playbackSummary;
    }

    void stop()
    {
        playing = false;
    }

    [[nodiscard]] bool isPlaying() const noexcept
    {
        return playing;
    }

    [[nodiscard]] bool isLoopEnabled() const noexcept
    {
        return loopEnabled;
    }

    [[nodiscard]] juce::String getCurrentSummary() const
    {
        return currentSummary;
    }

private:
    bool playing = false;
    bool loopEnabled = false;
    juce::String currentSummary;
};
} // namespace Engine
