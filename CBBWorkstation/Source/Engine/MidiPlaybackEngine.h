#pragma once

#include <juce_events/juce_events.h>

namespace Engine
{
class MidiPlaybackEngine
{
public:
    MidiPlaybackEngine() = default;

    void play()
    {
        // TODO: Connect generated MIDI events to a playback clock and output device.
    }

    void stop()
    {
        // TODO: Stop playback and reset transport state.
    }

    [[nodiscard]] bool isPlaying() const noexcept
    {
        return false;
    }
};
} // namespace Engine
