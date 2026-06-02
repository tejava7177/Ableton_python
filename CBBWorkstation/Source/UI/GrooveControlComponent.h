#pragma once

#include <functional>

#include <juce_gui_extra/juce_gui_extra.h>

class GrooveControlComponent final : public juce::Component
{
public:
    GrooveControlComponent();

    void paint(juce::Graphics& g) override;
    void resized() override;

    [[nodiscard]] float getEnergy() const noexcept;
    [[nodiscard]] float getSwing() const noexcept;
    void setOnGrooveChange(std::function<void()> callback);

private:
    juce::Label titleLabel;
    juce::Label energyLabel;
    juce::Label swingLabel;
    juce::Slider energySlider;
    juce::Slider swingSlider;
    std::function<void()> onGrooveChange;

    void configureSlider(juce::Slider& slider);

    JUCE_DECLARE_NON_COPYABLE_WITH_LEAK_DETECTOR(GrooveControlComponent)
};
