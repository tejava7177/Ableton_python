#pragma once

#include <juce_core/juce_core.h>

#include <vector>

#include "../Domain/Chord.h"

namespace Engine
{
class ChordParser
{
public:
    [[nodiscard]] static std::vector<Chord> parse(const juce::String& chordProgression)
    {
        std::vector<Chord> parsedChords;
        const auto tokens = juce::StringArray::fromTokens(chordProgression, "-", "");

        for (const auto& token : tokens)
        {
            const auto trimmed = token.trim();
            if (trimmed.isEmpty())
                continue;

            // TODO: expand this into a proper harmony parser.
            parsedChords.push_back({ trimmed, {} });
        }

        return parsedChords;
    }
};
} // namespace Engine
