/**
 * An anchor extension to the Wagtail editor, written by Thibaud
 * Colas, available at
 * https://github.com/thibaudcolas/wagtail_draftail_experiments
 */
const React = window.React;
const RichUtils = window.DraftJS.RichUtils;

/**
 * A React component that renders nothing.
 * We actually create the entities directly in the componentDidMount lifecycle hook.
 */
// Warning: This code uses ES2015+ syntax, it will not work in IE11.
class AnchorSource extends React.Component {
    componentDidMount() {
        const { editorState, entityType, onComplete } = this.props;

        const content = editorState.getCurrentContent();

        // This is very basic – we do not even support editing existing anchors.
        const fragment = window.prompt('Fragment identifier\n("#footnote-" followed by number, eg "#footnote-1"):');

        // Uses the Draft.js API to create a new entity with the right data.
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


class AnchorIDSource extends React.Component {
    componentDidMount() {
        const { editorState, entityType, onComplete } = this.props;

        const anchor_id = window.prompt('Anchor identifier (e.g., "footnote"):');

        const content = editorState.getCurrentContent();
        // Uses the Draft.js API to create a new entity with the right data.
        const contentWithEntity = content.createEntity(
            entityType.type,
            'IMMUTABLE',
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
    }

    render() {
        return null;
    }
}

const AnchorID = props => {
    const { entityKey, contentState } = props;
    const data = contentState.getEntity(entityKey).getData();

    return React.createElement(
        'a',
        {
            role: 'button',
            title: data.anchorid,
            onMouseUp: () => {
                window.alert(data.anchorid);
            },
        },
        props.children,
    );
};

window.draftail.registerPlugin({
    type: 'ANCHORID',
    source: AnchorIDSource,
    decorator: AnchorID,
});
