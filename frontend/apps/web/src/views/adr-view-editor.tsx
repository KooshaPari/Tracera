/* eslint-disable react/jsx-filename-extension */

import { ADREditor } from "@/components/specifications/adr/ADREditor";
import React from "react";

interface ADRDraft {
	consequences?: string;
	context?: string;
	decision?: string;
	title?: string;
}

interface ADRCreateMutation {
	mutate: (
		payload: {
			consequences: string;
			context: string;
			decision: string;
			projectId: string;
			title: string;
		},
		options?: {
			onSuccess?: () => void;
		},
	) => void;
}

interface ADRViewEditorProps {
	createADR: ADRCreateMutation;
	onClose: () => void;
	projectId: string;
}

const ADRViewEditor = ({
	createADR,
	onClose,
	projectId,
}: ADRViewEditorProps): JSX.Element => {
	const handleCancel = React.useCallback(() => {
		onClose();
	}, [onClose]);

	const handleSave = React.useCallback(
		(data: ADRDraft) => {
			createADR.mutate(
				{
					consequences: data.consequences || "",
					context: data.context || "",
					decision: data.decision || "",
					projectId,
					title: data.title || "",
				},
				{
					onSuccess: onClose,
				},
			);
		},
		[createADR, onClose, projectId],
	);

	return (
		<div className="p-6">
			<ADREditor onSave={handleSave} onCancel={handleCancel} />
		</div>
	);
};

// eslint-disable-next-line import/no-default-export
export default ADRViewEditor;
