

export function ArgsBox({selectedArgIdx, setSelectedArgIdx, args, setArgs}) {

    const rows = args.slice(1).map((arg_val, idx) => ArgRow(idx + 1, arg_val))

    return (
        <div tabIndex="2" className="args-box pl-10 dropdown" onKeyUp={(ev) => onArgsBoxKeyUp(ev, setSelectedArgIdx)}>
            <table>
                <tbody>
                    {ArgInputRow(selectedArgIdx, args, setArgs)}
                </tbody>
            </table>
            <table className="dropdown-content" style={{"paddingLeft": "0px"}}>
                <tbody>
                {rows}
                </tbody>
            </table>
        </div>
    )
}

function onArgsBoxKeyUp(ev, setSelectedArgIdx) {
    console.log(ev);
    if (ev.ctrlKey && ev.shiftKey) {
        for(let i=0; i<10; i++) {
            if(ev.key === `${i}`) {
                setSelectedArgIdx(i);
                break
            }
        }
    }

}

function ArgInputRow(idx, args, setArgs) {
    return (
        <tr className="arg-row">
            <td><input type="text" className='arg-input'
                     onChange={(ev) => onArgInputChange(ev, idx, setArgs, args)} >
                </input></td>
            <td className="arg-idx">arg[{idx }]</td><td>{args[idx]}</td>
        </tr>
    )
}

function onArgInputChange(ev, idx, setArgs, args) {
    let newArgs = [...args];
    newArgs[idx] = ev.target.value;
    console.log(`idx: ${idx} - setting args: ${newArgs}`);
    // console.log(ev);
    setArgs(newArgs)
}

function ArgRow(idx, arg_val) {
    return (
        <tr className="arg-row" key={idx}>
            <td className="arg-idx">arg: {idx}</td><td>{arg_val}</td>
        </tr>
    )
}
