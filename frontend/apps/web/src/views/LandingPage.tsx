import { Link } from "@tanstack/react-router";
import { ArrowRight, GitBranch, Layers, Zap } from "lucide-react";
import { Button } from "@/components/ui/enterprise-button";

export function LandingPage() {
	return (
		<div className="min-h-screen bg-background text-foreground flex flex-col">
			{/* Header / Nav */}
			<header className="py-4 px-6 border-b border-border/40 backdrop-blur-sm fixed top-0 w-full z-50 bg-background/80">
				<div className="container mx-auto flex justify-between items-center">
					<div className="flex items-center gap-2 font-bold text-xl">
						<div className="w-8 h-8 rounded-lg bg-primary flex items-center justify-center text-primary-foreground">
							T
						</div>
						TraceRTM
					</div>
					<div className="flex items-center gap-4">
						<Link
							to="/auth/login"
							className="text-sm font-medium hover:text-primary transition-all duration-200 ease-out active:scale-95"
						>
							Login
						</Link>
						<Link to="/auth/register">
							<Button size="sm" variant="enterprise">
								Get Started
							</Button>
						</Link>
					</div>
				</div>
			</header>

			<main className="flex-1 pt-24 animate-in-fade-up">
				{/* Hero Section */}
				<section className="py-20 px-6 relative overflow-hidden">
					{/* Background effects */}
					<div className="absolute top-0 left-1/2 -translate-x-1/2 w-full h-[500px] bg-primary/5 blur-[120px] rounded-full pointer-events-none" />

					<div className="container mx-auto text-center max-w-4xl relative z-10">
						<div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-primary/10 text-primary text-xs font-medium mb-8 border border-primary/20">
							<span className="relative flex h-2 w-2">
								<span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-primary opacity-75"></span>
								<span className="relative inline-flex rounded-full h-2 w-2 bg-primary"></span>
							</span>
							v2.0 Now Available
						</div>
						<h1 className="text-5xl md:text-7xl font-bold tracking-tight mb-6 bg-clip-text text-transparent bg-gradient-to-r from-foreground to-foreground/70">
							Requirements Traceability <br />
							<span className="text-primary">Reimagined</span>
						</h1>
						<p className="text-xl text-muted-foreground mb-10 max-w-2xl mx-auto leading-relaxed">
							End-to-end traceability from requirements to code. Visualize
							dependencies, ensure compliance, and ship with confidence.
						</p>
						<div className="flex flex-col sm:flex-row items-center justify-center gap-4">
							<Link to="/auth/register">
								<Button
									size="lg"
									variant="enterprise"
									className="min-w-[160px] h-12 text-base shadow-lg shadow-primary/20"
								>
									Start Free Trial
									<ArrowRight className="ml-2 w-4 h-4" />
								</Button>
							</Link>
							<Link to="/auth/login">
								<Button
									size="lg"
									variant="outline"
									className="min-w-[160px] h-12 text-base"
								>
									View Demo
								</Button>
							</Link>
						</div>

						<div className="mt-20 relative rounded-xl border border-border/50 bg-card/50 shadow-2xl overflow-hidden backdrop-blur-sm">
							<div className="absolute inset-0 bg-gradient-to-tr from-primary/5 to-transparent pointer-events-none" />
							{/* Placeholder for App Screenshot */}
							<div className="aspect-[16/9] flex items-center justify-center text-muted-foreground bg-muted/20">
								<div className="text-center p-8">
									<Layers className="w-16 h-16 mx-auto mb-4 opacity-50" />
									<p>Interactive Graph View Placeholder</p>
								</div>
							</div>
						</div>
					</div>
				</section>

				{/* Features Section */}
				<section className="py-24 px-6 bg-muted/30">
					<div className="container mx-auto max-w-6xl">
						<div className="text-center mb-16">
							<h2 className="text-3xl font-bold mb-4">Why TraceRTM?</h2>
							<p className="text-muted-foreground max-w-2xl mx-auto">
								Built for complex engineering teams who need total visibility
								and control.
							</p>
						</div>

						<div className="grid md:grid-cols-3 gap-8">
							<FeatureCard
								icon={<Layers className="w-6 h-6 text-blue-500" />}
								title="Multi-View Visualization"
								description="Switch instantly between Traceability Matrix, Dependency Graph, Kanban Board, and Tree Views."
							/>
							<FeatureCard
								icon={<Zap className="w-6 h-6 text-amber-500" />}
								title="AI-Powered Insights"
								description="Automatically detect missing requirements, compliance gaps, and contradictory specifications."
							/>
							<FeatureCard
								icon={<GitBranch className="w-6 h-6 text-green-500" />}
								title="Code Integration"
								description="Link requirements directly to PRs and commits. Keep documentation in sync with development."
							/>
						</div>
					</div>
				</section>
			</main>

			<footer className="py-8 px-6 border-t border-border/40 bg-background">
				<div className="container mx-auto flex flex-col md:flex-row justify-between items-center gap-4">
					<p className="text-sm text-muted-foreground">
						© 2026 TraceRTM. All rights reserved.
					</p>
					<div className="flex gap-6 text-sm text-muted-foreground">
						<Link to="#" className="hover:text-foreground">
							Privacy
						</Link>
						<Link to="#" className="hover:text-foreground">
							Terms
						</Link>
						<Link to="#" className="hover:text-foreground">
							Contact
						</Link>
					</div>
				</div>
			</footer>
		</div>
	);
}

function FeatureCard({
	icon,
	title,
	description,
}: {
	icon: React.ReactNode;
	title: string;
	description: string;
}) {
	return (
		<div className="p-6 rounded-2xl bg-card border border-border/50 shadow-sm hover:shadow-md transition-all hover:-translate-y-1">
			<div className="w-12 h-12 rounded-lg bg-background border border-border flex items-center justify-center mb-4">
				{icon}
			</div>
			<h3 className="text-xl font-bold mb-2">{title}</h3>
			<p className="text-muted-foreground leading-relaxed">{description}</p>
		</div>
	);
}
