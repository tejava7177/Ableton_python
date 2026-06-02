#pragma once

#include <juce_gui_extra/juce_gui_extra.h>

#include "Domain/Style.h"
#include "Engine/MidiPlaybackEngine.h"
#include "Engine/PatternGenerator.h"
#include "UI/BackingSummaryComponent.h"
#include "UI/ChordInputComponent.h"
#include "UI/GrooveControlComponent.h"
#include "UI/SectionPanelComponent.h"
#include "UI/TransportComponent.h"

class MainComponent final : public juce::Component
{
public:
    MainComponent();

    void paint(juce::Graphics& g) override;
    void resized() override;

private:
    juce::Label titleLabel;
    juce::Label subtitleLabel;
    juce::Label styleLabel;
    juce::ComboBox styleSelector;
    juce::Label optionsHintLabel;

    ChordInputComponent chordInputComponent;
    SectionPanelComponent sectionPanelComponent;
    GrooveControlComponent grooveControlComponent;
    BackingSummaryComponent backingSummaryComponent;
    TransportComponent transportComponent;
    Engine::PatternGenerator patternGenerator;
    Engine::MidiPlaybackEngine playbackEngine;

    void refreshGeneratedPreview();
    void generateBacking(bool shouldStartPlayback);
    [[nodiscard]] StyleType getSelectedStyle() const noexcept;
    [[nodiscard]] juce::String getSectionText() const;
    [[nodiscard]] juce::String getEnergyText() const;
    [[nodiscard]] juce::String getSwingText() const;

    JUCE_DECLARE_NON_COPYABLE_WITH_LEAK_DETECTOR(MainComponent)
};
