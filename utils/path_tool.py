'''
为整个工程提供统一的绝对路径
'''
import os

def get_project_root()->str:
    '''
     获取工程所在的根目录
     ：return：字符串根目录
    '''
    # 当前文件的绝对路径
    current_file=os.path.abspath(__file__)
    current_dir=os.path.dirname(current_file)
    project_root=os.path.dirname(current_dir)
    return project_root

def get_abs_path(relative_path:str)->str:
    ''' 
    传入一个相对路径（比如 "config/rag.yml"），返回一个完整的绝对路径
    :param relative_path: 相对路径，例如 "config/rag.yml"
    :return: 绝对路径，例如 "/Users/xxx/LangChain-ReAct-Agent/config/rag.yml"
    '''
    project_root=get_project_root()
    return os.path.join(project_root,relative_path)


if __name__=='__main__':
    print(get_abs_path("config/rag.yml"))