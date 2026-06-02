#pragma once

#include <juce_core/juce_core.h>

#include <optional>
#include <vector>

#include "../Domain/Chord.h"

namespace Engine
{
struct ParsedChordProgression
{
    bool isValid = false;
    juce::String message;
    std::vector<Chord> chords;
};

class ChordParser
{
public:
    [[nodiscard]] static ParsedChordProgression parse(const juce::String& chordProgression)
    {
        ParsedChordProgression result;
        const auto tokens = juce::StringArray::fromTokens(chordProgression, "-", "");

        for (const auto& token : tokens)
        {
            const auto trimmed = token.trim();
            if (trimmed.isEmpty())
                continue;

            if (auto parsedChord = parseChordToken(trimmed))
            {
                result.chords.push_back(*parsedChord);
                continue;
            }

            result.message = "Unsupported chord token: " + trimmed;
            return result;
        }

        if (result.chords.empty())
        {
            result.message = "Enter at least one chord progression token.";
            return result;
        }

        result.isValid = true;
        result.message = "Parsed " + juce::String(result.chords.size()) + " chords.";
        return result;
    }

private:
    [[nodiscard]] static std::optional<Chord> parseChordToken(const juce::String& token)
    {
        const auto trimmed = token.trim();
        if (trimmed.isEmpty())
            return std::nullopt;

        const auto normalized = trimmed.removeCharacters(" ");
        auto rootLength = 1;

        if (normalized.length() >= 2)
        {
            const auto accidental = normalized[1];
            if (accidental == '#' || accidental == 'b')
                rootLength = 2;
        }

        const auto root = normalized.substring(0, rootLength);
        const auto quality = normalized.substring(rootLength);

        if (auto midiRoot = rootToMidi(root))
        {
            Chord chord;
            chord.symbol = normalized;
            chord.root = root;
            chord.quality = quality;
            chord.midiRoot = *midiRoot;
            return chord;
        }

        return std::nullopt;
    }

    [[nodiscard]] static std::optional<int> rootToMidi(const juce::String& root)
    {
        const auto upperRoot = root.toUpperCase();

        if (upperRoot == "C") return 60;
        if (upperRoot == "C#" || upperRoot == "DB") return 61;
        if (upperRoot == "D") return 62;
        if (upperRoot == "D#" || upperRoot == "EB") return 63;
        if (upperRoot == "E") return 64;
        if (upperRoot == "F") return 65;
        if (upperRoot == "F#" || upperRoot == "GB") return 66;
        if (upperRoot == "G") return 67;
        if (upperRoot == "G#" || upperRoot == "AB") return 68;
        if (upperRoot == "A") return 69;
        if (upperRoot == "A#" || upperRoot == "BB") return 70;
        if (upperRoot == "B") return 71;

        return std::nullopt;
    }
};
} // namespace Engine
