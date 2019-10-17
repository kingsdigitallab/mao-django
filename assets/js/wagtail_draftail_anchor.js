/**
 * An anchor extension to the Wagtail editor, written by Thibaud
 * Colas, available at
 * https://github.com/thibaudcolas/wagtail_draftail_experiments
 */
const React = window.React;
const RichUtils = window.DraftJS.RichUtils;
const DraftailEditor = window.DraftJS.DraftailEditor;

// Warning: This code uses ES2015+ syntax, it will not work in IE11.
class AnchorSource extends React.Component {
    componentDidMount() {
        const { editorState, entityType, onComplete } = this.props;

        const content = editorState.getCurrentContent();

        const fragment = window.prompt('Fragment identifier\n("#footnote-" followed by number, eg "#footnote-1"):');

        const contentWithEntity = content.createEntity(
            entityType.type,
            'MUTABLE',
            {
                fragment: fragment,
            },
        );
        const entityKey = contentWithEntity.getLastCreatedEntityKey();
        const selection = editorState.getSelection();
        const nextState = RichUtils.toggleLink(
            editorState,
            selection,
            entityKey,
        );

        onComplete(nextState);
    }

    render() {
        return null;
    }
}

const Anchor = props => {
    const { entityKey, contentState } = props;
    const data = contentState.getEntity(entityKey).getData();

    return React.createElement(
        'a',
        {
            role: 'button',
            title: data.fragment,
            onMouseUp: () => {
                window.alert(data.fragment);
            },
        },
        props.children,
    );
};

window.draftail.registerPlugin({
    type: 'ANCHOR',
    source: AnchorSource,
    decorator: Anchor,
});



/* An extension of extension developed by King's Digital Lab
   to connect anchors with html blocks through id's
*/
class AnchorIDSource extends React.Component {
    componentDidMount() {
        const { editorState, entityType, onComplete } = this.props;
        
        const anchor_id = window.prompt('Anchor identifier (e.g., "footnote").\nPlease ensure that two different sections don\'t have the same identifier:');

        if (anchor_id) {
            const content = editorState.getCurrentContent();
            // Uses the Draft.js API to create a new entity with the right data.
            const contentWithEntity = content.createEntity(
                entityType.type,
                'MUTABLE',
                {
                    anchorid: anchor_id,
                },
            );
            const entityKey = contentWithEntity.getLastCreatedEntityKey();
            const selection = editorState.getSelection();
            const nextState = RichUtils.toggleLink(
                editorState,
                selection,
                entityKey,
            );

            onComplete(nextState);
        } else {
            onComplete(editorState);
        }
    }

    render() {
        return null;
    }
}

const AnchorID = props => {
    const { entityKey, contentState, onEdit, onRemove } = props;
    const data = contentState.getEntity(entityKey).getData();


    remove = (e) => {
        e.preventDefault();
        e.stopPropagation();
        onRemove(entityKey);
    }
    edit = (e) => {
        e.preventDefault();
        e.stopPropagation();
        onEdit(entityKey);
    }
    return React.createElement(
        'a',
        {
            role: "button",
            title: data.anchorid,
            "data-draftail-trigger": "true",
            style: {
                "cursor": "pointer",
                "color": "green"
            },
            onClick: (t) => {
                var e = t.target.closest("[data-draftail-trigger]");
                if (e) {
                    var n = e.closest("[data-draftail-editor-wrapper]"),
                    r = n.getBoundingClientRect(),
                    o = e.getBoundingClientRect();
                    var x = document.getElementById("data-editor-"+data.anchorid);
                    if (x.style.display === "none") {
                        x.style.display = "block";
                        x.style.left = o.left - r.left + 30 - (document.documentElement.scrollLeft || document.body.scrollLeft) + "px";
                    } else {
                        x.style.display = "none";
                    }
                }
            }
        }, 
        props.children,
        React.createElement(
            'div',
            {
                id: "data-editor-"+data.anchorid,
                className: "Tooltip Tooltip--top",
                role: "tooltip",
                style: {
                    "display": "none",
                    "font-size": "14px",
                }
            },
            data.anchorid,
            React.createElement(
                'button',
                {
                    className: "button Tooltip__button",
                    style: {
                        "margin-left": "20px"
                    },
                    onClick: this.edit
                },
                "edit"
            ),
            React.createElement(
                'button',
                {
                    className: "button button-secondary no Tooltip__button",
                    onClick: this.remove
                },
                "remove"
            )
        )
    );

};

window.draftail.registerPlugin({
    type: 'ANCHORID',
    source: AnchorIDSource,
    decorator: AnchorID,
});
