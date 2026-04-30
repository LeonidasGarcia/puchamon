interface SectionProps {
  label?: string;
  children?: React.ReactNode;
}

export default function Section(props: SectionProps) {
  return (
    <div className="px-6 flex flex-col gap-5">
      <p className="text-body/[24px]">{props.label}</p>
      {props.children && (
        <div className="flex gap-4 justify-center">{props.children}</div>
      )}
    </div>
  );
}
