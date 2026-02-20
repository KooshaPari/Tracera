import { HeroSection } from "@/components/hero-section"
import { FeaturesSection } from "@/components/features-section"
import { QuickLinks } from "@/components/quick-links"
import { StatsSection } from "@/components/stats-section"

export default function Home() {
  return (
    <>
      <HeroSection />
      <FeaturesSection />
      <QuickLinks />
      <StatsSection />
    </>
  )
}
