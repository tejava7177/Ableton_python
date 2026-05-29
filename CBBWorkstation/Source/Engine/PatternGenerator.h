#pragma once

#include "../Domain/Section.h"
#include "../Domain/Style.h"

namespace Engine
{
class PatternGenerator
{
public:
    PatternGenerator() = default;

    void prepare(StyleType, SectionType)
    {
        // TODO: Generate beginner-friendly backing patterns for the selected style and section.
    }
};
} // namespace Engine

