#pragma once

#include <juce_gui_extra/juce_gui_extra.h>

#include "Domain/Style.h"
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

    ChordInputComponent chordInputComponent;
    SectionPanelComponent sectionPanelComponent;
    GrooveControlComponent grooveControlComponent;
    TransportComponent transportComponent;

    JUCE_DECLARE_NON_COPYABLE_WITH_LEAK_DETECTOR(MainComponent)
};
