#pragma once

#include <functional>

#include <juce_gui_extra/juce_gui_extra.h>

#include "../Domain/Section.h"

class SectionPanelComponent final : public juce::Component
{
public:
    SectionPanelComponent();

    void paint(juce::Graphics& g) override;
    void resized() override;

    [[nodiscard]] SectionType getSelectedSection() const noexcept;
    void setOnSectionChange(std::function<void(SectionType)> callback);

private:
    juce::Label titleLabel;
    juce::TextButton mainAButton { "Main A" };
    juce::TextButton fillButton { "Fill" };
    juce::TextButton endingButton { "Ending" };
    std::function<void(SectionType)> onSectionChange;

    void selectSection(SectionType section);

    JUCE_DECLARE_NON_COPYABLE_WITH_LEAK_DETECTOR(SectionPanelComponent)
};
