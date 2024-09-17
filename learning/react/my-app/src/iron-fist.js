import { useState } from 'react';
import { ArgsBox } from './args';

const fillTemplate = require('es6-dynamic-template');


const CMD_TMPLS_AWS_EKS = {
    "sso-login": {bound_key: "L", label: "SSO Login", tmpl: "aws sso login ${arg1}" },
    "s3-ls" : {bound_key: "l", label: "S3 ls", tmpl: "aws s3 ls ${arg1}" }
}

const CMD_TMPLS_SYS_ADMIN = {
    "ls": {bound_key: "l", label: "List dir contents", tmpl: "ls -l" },
    "mkdir": {bound_key: "D", label: "Make directory", tmpl: "mkdir {arg1}" }
}

const CMD_TMPLS_GIT = {
    "status": {bound_key: "s", label: "git status", tmpl: "git status" }
}

const CMD_GROUPS = {
    "aws-eks": {bound_key: "a", label: "AWS / EKS", tmpls: CMD_TMPLS_AWS_EKS},
    "sys-admin": {bound_key: "S", label: "System Admin", tmpls: CMD_TMPLS_SYS_ADMIN},
    "git": {bound_key: "g", label: "Git", tmpls: CMD_TMPLS_GIT},
};



export default function App() {
    const [selectedGrpKey, setSelectedGrpKey] = useState("sys-admin")
    const [activePannel, setActivePannel] = useState("selector")
    const [choices, setChoices] = useState(CMD_GROUPS)
    const [choiceTarget, setChoiceTarget] = useState("cmd-group")
    const [tmpl, setTmpl] = useState("")
    const [cmd, setCmd] = useState("")
    const [msg, setMsg] = useState("Welcome to IronFist Commander!")
    const [args, setArgs] = useState([null, null, null])
    const [selectedArgIdx, setSelectedArgIdx] = useState(1)

    const state={
        selectedGrpKey, setSelectedGrpKey,
        activePannel, setActivePannel,
        choices, setChoices,
        choiceTarget, setChoiceTarget,
        msg, setMsg,
        tmpl, setTmpl,
        cmd, setCmd,
        args, setArgs,
        selectedArgIdx, setSelectedArgIdx,
    };
    return (<MainWindow state={state} />);
}


function MainWindow({state}) {
    return (
        <div className="main-grid">
            <SelectByKey state={state} />
            <MsgLine msg={state.msg}/>
            <ArgsBox
                selectedArgIdx={state.selectedArgIdx}
                setSelectedArgIdx={state.setSelectedArgIdx}
                args={state.args} setArgs={state.setArgs}/>
            <CmdLine tabindex="2" cmd={state.cmd}/>
            <CmdOutput state={state}/>
        </div>
    )
}


function SelectByKey({state}) {
    const rows = [];
    for (const [key, choice] of Object.entries(state.choices)) {
        rows.push(
            <ChoiceRow
                label={choice.label}
                bound_key={choice.bound_key}
                key={key}
            />
        );
    };

    return (
        <div tabIndex="0" className="selector"
            onKeyUp={(ev) => handleKeyPressGroup(state, ev)}>
        <table>
            <tbody>
                {rows}
            </tbody>
        </table>
        </div>
    )
}

function handleKeyPressGroup(state, event) {
    let key = event.key;

    console.log(`handleKeyPressGroup key=${key}`);

    Object.entries(state.choices).forEach( ([choice_key, grp]) => {
        if (grp.bound_key === key) {
            if (state.choiceTarget === "cmd-group") {
                state.setSelectedGrpKey(choice_key);
                state.setChoices(grp.tmpls);
                state.setMsg(`selected group: ${grp.label}`);
                state.setChoiceTarget("cmd-tmpl");
            } else if (state.choiceTarget === "cmd-tmpl") {
                state.setTmpl(grp.tmpl);
                state.setMsg(`${CMD_GROUPS[state.selectedGrpKey].label} | ${grp.label}: ${grp.tmpl}`)
                console.log({tmpl: grp.tmpl, arg: state.args});
                const args_dict= Object.fromEntries( state.args.map( (v, i) => [`arg${i}`, v] ) );
                state.setCmd( fillTemplate(grp.tmpl, args_dict));
            }
        }
    });
}


function ChoiceRow({label, bound_key}) {
    let classes = "key-binding kb-active";
    return (
        <tr className="cmd-group-row">
            <td className={classes}>{bound_key}</td><td style={{"paddingLeft": "5px"}}>{label}</td>
        </tr>
    );
}


function MsgLine({msg}) {
    return (
        <p tabIndex="1" className="msg-line no-margin-block pl-10">{msg}</p>
    )
}

function CmdLine({cmd}) {
    return (
        <p tabIndex="3" className="cmd-line no-margin-block pl-10">{cmd}</p>
    );
}

function CmdOutput({state}) {
    return (
        <pre className="cmd-output pl-10 no-margin-block">
            Command output would
            come here
        </pre>

    )
}