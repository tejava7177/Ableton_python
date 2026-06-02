#pragma once

#include <juce_core/juce_core.h>

#include <vector>

#include "../Domain/Chord.h"
#include "../Domain/Section.h"
#include "../Domain/Style.h"

namespace Engine
{
struct GeneratedPattern
{
    juce::String drumPattern;
    juce::String bassPattern;
    juce::String description;
};

class PatternGenerator
{
public:
    PatternGenerator() = default;

    [[nodiscard]] GeneratedPattern prepare(const std::vector<Chord>& chords,
                                           StyleType style,
                                           SectionType section,
                                           float energy,
                                           float swing) const
    {
        GeneratedPattern pattern;

        const auto chordCount = juce::String(static_cast<int>(chords.size()));
        const auto sectionName = toSectionName(section);
        const auto styleName = toStyleName(style);
        const auto energyName = describeEnergy(energy);
        const auto swingName = describeSwing(swing);

        if (style == StyleType::Blues)
        {
            pattern.drumPattern = section == SectionType::Fill ? "Shuffle fill accents" : "Shuffle backbeat";
            pattern.bassPattern = "Walking root-fifth variation";
        }
        else if (style == StyleType::Ballad)
        {
            pattern.drumPattern = section == SectionType::Ending ? "Sparse cymbal ending" : "Soft straight ballad";
            pattern.bassPattern = "Sustained root motion";
        }
        else if (style == StyleType::JPop)
        {
            pattern.drumPattern = section == SectionType::Fill ? "Bright tom fill" : "Tight pop groove";
            pattern.bassPattern = "Active eighth-note support";
        }
        else
        {
            pattern.drumPattern = section == SectionType::Ending ? "Straight pop ending" : "Straight pop groove";
            pattern.bassPattern = "Root-fifth pop pulse";
        }

        pattern.description = styleName + " / " + sectionName
            + " / " + chordCount + " chords / "
            + energyName + " energy / "
            + swingName + " swing";

        return pattern;
    }

private:
    [[nodiscard]] static juce::String toStyleName(StyleType style)
    {
        switch (style)
        {
            case StyleType::Pop: return "Pop";
            case StyleType::JPop: return "J-Pop";
            case StyleType::Blues: return "Blues";
            case StyleType::Ballad: return "Ballad";
        }

        return "Unknown";
    }

    [[nodiscard]] static juce::String toSectionName(SectionType section)
    {
        switch (section)
        {
            case SectionType::MainA: return "Main A";
            case SectionType::Fill: return "Fill";
            case SectionType::Ending: return "Ending";
        }

        return "Unknown";
    }

    [[nodiscard]] static juce::String describeEnergy(float energy)
    {
        if (energy < 0.34f)
            return "Low";
        if (energy < 0.67f)
            return "Medium";
        return "High";
    }

    [[nodiscard]] static juce::String describeSwing(float swing)
    {
        if (swing < 0.2f)
            return "Straight";
        if (swing < 0.6f)
            return "Light";
        return "Heavy";
    }
};
} // namespace Engine
