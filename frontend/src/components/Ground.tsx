interface GroundProps {}

export default function Ground(
  props: GroundProps & React.HTMLAttributes<HTMLDivElement>,
) {
  return (
    <div className={`"flex w-68 h-16 " ${props.className}`}>
      <div className="flex-1 h-full bg-[#B2B293] border-6 box-border border-[#C9C7B2] rounded-[50%/50%]"></div>
    </div>
  );
}
